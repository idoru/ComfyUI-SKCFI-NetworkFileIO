import requests
import os
import time
from typing import List, Tuple, Any
from pathlib import Path


class FilestashUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
                "filestash_url": ("STRING", {"default": "http://localhost:8334"}),
                "api_key": ("STRING", {"default": ""}),
                "share_id": ("STRING", {"default": ""}),
                "upload_path": ("STRING", {"default": "/uploads/"}),
            },
            "optional": {
                "log_file": ("STRING", {"default": ""}),
                "extra_headers": ("STRING", {"multiline": True, "default": ""}),
            },
        }

    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("status_code", "result_text")
    FUNCTION = "upload_file"
    CATEGORY = "file_operations"

    def upload_file(
        self,
        file_path: str,
        filestash_url: str,
        api_key: str,
        share_id: str,
        upload_path: str,
        log_file: str = "",
        extra_headers: str = "",
    ) -> Tuple[int, str]:
        """
        Upload single file to Filestash server with retry logic and optional failure logging

        Args:
            file_path: Path to the single file to upload
            filestash_url: Base URL of Filestash instance
            api_key: API key for authentication
            share_id: Share ID for the upload location
            upload_path: Destination path on Filestash server
            log_file: Optional path to log failed uploads
            extra_headers: Optional HTTP headers (one per line, format: "Header-Name: value")

        Returns:
            Tuple of (status_code, result_text)
        """
        if not file_path.strip():
            return (400, "File path is required")

        if not api_key or not share_id:
            return (400, "API key and Share ID are required")

        if not os.path.exists(file_path):
            return (404, f"File not found: {file_path}")

        # Parse extra headers
        headers = self._parse_headers(extra_headers)

        # Set up SSL certificate path once
        cert_paths = [
            "/etc/ssl/certs/ca-certificates.crt",  # Common Linux location
            "/usr/lib/ssl/cert.pem",  # Default SSL path
        ]

        cert_path = None
        for path in cert_paths:
            if os.path.exists(path):
                cert_path = path
                break

        # Use system default if no cert path found
        if cert_path is None:
            cert_path = True  # Use system default as last resort

        # Get filename from path
        filename = os.path.basename(file_path)

        # Construct destination path
        dest_path = upload_path.rstrip("/") + "/" + filename

        # Prepare API endpoint
        api_endpoint = f"{filestash_url.rstrip('/')}/api/files/cat"
        params = {"path": dest_path, "key": api_key, "share": share_id}

        # Attempt upload with retries
        last_error = None

        # Create a session with proper SSL context
        session = requests.Session()
        session.verify = cert_path

        for attempt in range(3):
            try:
                # Add delay between retries (except first attempt)
                if attempt > 0:
                    time.sleep(1 * attempt)  # 1s, 2s delays

                with open(file_path, "rb") as file:
                    response = session.post(
                        api_endpoint,
                        params=params,
                        data=file,
                        headers=headers,
                        timeout=30,
                    )

                # Log failed upload if log_file is specified and upload failed
                if response.status_code != 200 and log_file.strip():
                    self._log_failed_uploads(log_file.strip(), [file_path])

                return (response.status_code, response.text)

            except requests.RequestException as e:
                last_error = f"Network error: {str(e)}"
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"

        # If we get here, all retries failed
        if log_file.strip():
            self._log_failed_uploads(log_file.strip(), [file_path])

        return (500, f"Upload failed after 3 attempts - {last_error}")

    def _log_failed_uploads(self, log_file_path: str, failed_files: List[str]):
        """Log failed upload file paths to the specified log file"""
        try:
            # Create parent directories if they don't exist
            log_path = Path(log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            # Append failed files to log
            with open(log_file_path, "a", encoding="utf-8") as f:
                timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
                f.write(f"\n# Failed uploads at {timestamp}\n")
                for failed_file in failed_files:
                    f.write(f"{failed_file}\n")

        except Exception as e:
            # Don't fail the entire operation if logging fails
            print(f"Warning: Could not write to log file {log_file_path}: {e}")

    def _parse_headers(self, extra_headers: str) -> dict:
        """Parse extra headers from multiline string format"""
        headers = {}
        if not extra_headers.strip():
            return headers

        for line in extra_headers.strip().split("\n"):
            line = line.strip()
            if not line or ":" not in line:
                continue

            try:
                key, value = line.split(":", 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    headers[key] = value
            except ValueError:
                # Skip malformed header lines
                continue

        return headers
