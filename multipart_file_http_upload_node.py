import requests
import os
import json
import time
import mimetypes
from typing import Tuple, Dict, Any
from pathlib import Path


class MultipartFileHTTPUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
                "url": ("STRING", {"default": "http://localhost:8000/upload"}),
                "method": (["POST", "PUT"], {"default": "POST"}),
                "upload_field_name": ("STRING", {"default": "file"}),
            },
            "optional": {
                "headers": ("STRING", {"multiline": True, "default": ""}),
                "secret_headers_file": ("STRING", {"default": ""}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
                "retry_count": ("INT", {"default": 3, "min": 1, "max": 3}),
                "retry_delay": ("INT", {"default": 1, "min": 1, "max": 3}),
            },
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("status_code", "result_text")
    FUNCTION = "send_multipart_http"
    CATEGORY = "file_operations"

    def send_multipart_http(
        self,
        file_path: str,
        url: str,
        method: str = "POST",
        upload_field_name: str = "file",
        headers: str = "",
        secret_headers_file: str = "",
        timeout: int = 30,
        retry_count: int = 3,
        retry_delay: int = 1,
    ) -> Tuple[int, str]:
        """
        Send file via multipart HTTP POST/PUT request with configurable retry logic
        and secure secret headers support

        Args:
            file_path: Path to the file to upload
            url: Target URL for HTTP request
            method: HTTP method (POST or PUT)
            upload_field_name: Name of the multipart form field for the file
            headers: Optional HTTP headers (multiline key:value format)
            secret_headers_file: Path to JSON file containing secret headers
            timeout: Request timeout in seconds
            retry_count: Number of retry attempts
            retry_delay: Base delay between retries in seconds

        Returns:
            Tuple of (status_code, result_text)
        """
        # Input validation
        if not file_path.strip():
            return (400, "File path is required")

        if not url.strip():
            return (400, "URL is required")

        if not upload_field_name.strip():
            return (400, "Upload field name is required")

        if not os.path.exists(file_path):
            return (404, f"File not found: {file_path}")

        # Parse headers securely
        try:
            parsed_headers = self._parse_headers_securely(headers, secret_headers_file)
        except Exception as e:
            # Sanitize error message to avoid exposing secret file contents
            return (400, f"Header parsing error - check configuration")

        # Detect MIME type
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            # Default to binary for video files and unknown types
            mime_type = "application/octet-stream"

        filename = os.path.basename(file_path)

        # Attempt upload with configurable retries
        last_error = None

        for attempt in range(retry_count):
            try:
                # Add progressive delay between retries (except first attempt)
                if attempt > 0:
                    time.sleep(retry_delay * attempt)

                # Prepare file for multipart upload
                with open(file_path, "rb") as f:
                    files_data = {upload_field_name: (filename, f, mime_type)}

                    # Make HTTP request
                    if method.upper() == "POST":
                        response = requests.post(
                            url,
                            files=files_data,
                            headers=parsed_headers,
                            timeout=timeout,
                        )
                    else:  # PUT
                        response = requests.put(
                            url,
                            files=files_data,
                            headers=parsed_headers,
                            timeout=timeout,
                        )

                # Return successful response immediately
                return (response.status_code, response.text)

            except requests.exceptions.Timeout:
                last_error = f"Request timeout after {timeout} seconds"
            except requests.exceptions.ConnectionError:
                last_error = f"Connection error: Unable to connect to {url}"
            except requests.exceptions.RequestException as e:
                # Sanitize error message to avoid exposing sensitive information
                last_error = f"HTTP request error: {self._sanitize_error_message(str(e))}"
            except Exception as e:
                last_error = f"Unexpected error: {self._sanitize_error_message(str(e))}"

        # If we get here, all retries failed - log ERROR with full filepath
        error_msg = f"Upload failed after {retry_count} attempts - {last_error}"
        print(f"ERROR: Failed to upload file: {file_path} - {error_msg}")
        return (500, error_msg)

    def _parse_headers_securely(self, headers: str, secret_headers_file: str) -> Dict[str, str]:
        """
        Parse headers from regular headers string and secret headers file
        Secret headers override regular headers if there are conflicts
        """
        parsed_headers = {}

        # Parse regular headers first
        if headers.strip():
            parsed_headers = self._parse_headers(headers)

        # Parse secret headers from file if specified
        if secret_headers_file.strip():
            secret_headers = self._load_secret_headers(secret_headers_file.strip())
            # Merge secret headers (they take precedence)
            parsed_headers.update(secret_headers)

        return parsed_headers

    def _parse_headers(self, headers: str) -> Dict[str, str]:
        """
        Parse headers from either JSON string or multiline key:value format
        """
        if not headers.strip():
            return {}

        parsed_headers = {}
        headers_text = headers.strip()

        # Try to parse as JSON first
        try:
            if headers_text.startswith("{") and headers_text.endswith("}"):
                parsed_headers = json.loads(headers_text)
                if isinstance(parsed_headers, dict):
                    return parsed_headers
        except json.JSONDecodeError:
            pass

        # Parse as multiline key:value format
        for line in headers_text.split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue

            try:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    parsed_headers[key] = value
            except ValueError:
                continue

        return parsed_headers

    def _load_secret_headers(self, secret_file_path: str) -> Dict[str, str]:
        """
        Load secret headers from JSON file
        Returns empty dict if file doesn't exist or can't be parsed
        """
        try:
            if not os.path.exists(secret_file_path):
                raise FileNotFoundError(f"Secret headers file not found: {secret_file_path}")

            with open(secret_file_path, "r", encoding="utf-8") as f:
                secret_data = json.load(f)

            if not isinstance(secret_data, dict):
                raise ValueError("Secret headers file must contain a JSON object")

            # Ensure all keys and values are strings
            return {str(k): str(v) for k, v in secret_data.items()}

        except Exception as e:
            # Re-raise with sanitized message
            raise Exception(f"Failed to load secret headers")

    def _sanitize_error_message(self, error_msg: str) -> str:
        """
        Sanitize error messages to avoid exposing sensitive information
        """
        # Remove common sensitive patterns
        sensitive_patterns = [
            "Authorization:",
            "Bearer ",
            "api-key:",
            "x-api-key:",
            "token:",
            "password:",
            "secret:",
        ]

        sanitized_msg = error_msg
        for pattern in sensitive_patterns:
            # Replace the pattern and everything after it on the same line with [REDACTED]
            if pattern.lower() in sanitized_msg.lower():
                # Find the position and redact from there to end of line
                lines = sanitized_msg.split('\n')
                for i, line in enumerate(lines):
                    if pattern.lower() in line.lower():
                        idx = line.lower().find(pattern.lower())
                        lines[i] = line[:idx] + "[REDACTED]"
                sanitized_msg = '\n'.join(lines)

        return sanitized_msg