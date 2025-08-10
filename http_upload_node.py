import requests
import os
import json
from typing import Tuple, Any
from pathlib import Path


class HttpUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {"default": ""}),
                "url": ("STRING", {"default": "http://localhost:8000/upload"}),
                "method": (["POST", "PUT"], {"default": "POST"}),
            },
            "optional": {
                "headers": ("STRING", {"multiline": True, "default": ""}),
                "timeout": ("INT", {"default": 30, "min": 1, "max": 300}),
            }
        }
    
    RETURN_TYPES = ("INT", "STRING")
    RETURN_NAMES = ("status_code", "result_text")
    FUNCTION = "send_http"
    CATEGORY = "file_operations"

    def send_http(self, file_path: str, url: str, method: str = "POST", headers: str = "", timeout: int = 30) -> Tuple[int, str]:
        """
        Send single file via HTTP POST/PUT request, similar to WAS Image Send HTTP but for file uploads
        
        Args:
            file_path: Path to the single file to upload
            url: Target URL for HTTP request
            method: HTTP method (POST or PUT)
            headers: Optional HTTP headers (JSON string or multiline key:value format)
            timeout: Request timeout in seconds
        
        Returns:
            Tuple of (status_code, result_text)
        """
        if not file_path.strip():
            return (400, "File path is required")
        
        if not url.strip():
            return (400, "URL is required")
        
        if not os.path.exists(file_path):
            return (404, f"File not found: {file_path}")
        
        # Parse headers
        parsed_headers = self._parse_headers(headers)
        
        try:
            filename = os.path.basename(file_path)
            
            # Prepare file for upload
            with open(file_path, 'rb') as f:
                files_data = {'file': (filename, f, 'application/octet-stream')}
                
                # Make HTTP request
                if method.upper() == "POST":
                    response = requests.post(
                        url,
                        files=files_data,
                        headers=parsed_headers,
                        timeout=timeout
                    )
                else:  # PUT
                    response = requests.put(
                        url,
                        files=files_data,
                        headers=parsed_headers,
                        timeout=timeout
                    )
            
            return (response.status_code, response.text)
            
        except requests.exceptions.Timeout:
            return (408, f"Request timeout after {timeout} seconds")
        except requests.exceptions.ConnectionError:
            return (503, f"Connection error: Unable to connect to {url}")
        except requests.exceptions.RequestException as e:
            return (500, f"HTTP request error: {str(e)}")
        except Exception as e:
            return (500, f"Unexpected error: {str(e)}")
    
    def _parse_headers(self, headers: str) -> dict:
        """
        Parse headers from either JSON string or multiline key:value format
        Supports loading from WAS Load Text File node output
        """
        if not headers.strip():
            return {}
        
        parsed_headers = {}
        headers_text = headers.strip()
        
        # Try to parse as JSON first (from Load Text File node)
        try:
            if headers_text.startswith('{') and headers_text.endswith('}'):
                parsed_headers = json.loads(headers_text)
                if isinstance(parsed_headers, dict):
                    return parsed_headers
        except json.JSONDecodeError:
            pass
        
        # Parse as multiline key:value format
        for line in headers_text.split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            try:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    parsed_headers[key] = value
            except ValueError:
                continue
        
        return parsed_headers