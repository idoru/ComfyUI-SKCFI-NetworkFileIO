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
                "filenames": ("VHS_FILENAMES",),
                "filestash_url": ("STRING", {"default": "http://localhost:8334"}),
                "api_key": ("STRING", {"default": ""}),
                "share_id": ("STRING", {"default": ""}),
                "upload_path": ("STRING", {"default": "/uploads/"}),
            },
            "optional": {
                "log_file": ("STRING", {"default": ""}),
                "extra_headers": ("STRING", {"multiline": True, "default": ""}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("upload_results",)
    FUNCTION = "upload_files"
    CATEGORY = "file_operations"

    def upload_files(self, filenames, filestash_url: str, api_key: str, share_id: str, upload_path: str, log_file: str = "", extra_headers: str = "") -> Tuple[str]:
        """
        Upload files to Filestash server with retry logic and optional failure logging
        
        Args:
            filenames: VHS_FILENAMES from VideoCombine node - tuple containing (save_output_flag, list_of_file_paths)
            filestash_url: Base URL of Filestash instance
            api_key: API key for authentication
            share_id: Share ID for the upload location
            upload_path: Destination path on Filestash server
            log_file: Optional path to log failed uploads
            extra_headers: Optional HTTP headers (one per line, format: "Header-Name: value")
        
        Returns:
            String containing upload results
        """
        # Extract file list from VHS_FILENAMES tuple
        # filenames is a tuple: (save_output_flag, list_of_file_paths)
        if not filenames or len(filenames) < 2 or not filenames[1]:
            return ("No filenames provided from VideoCombine output",)
        
        if not api_key or not share_id:
            return ("API key and Share ID are required",)
        
        file_list = filenames[1]  # Extract the list of file paths from the VHS_FILENAMES tuple
        results = []
        failed_files = []
        
        # Parse extra headers
        headers = self._parse_headers(extra_headers)
        
        # Set up SSL certificate path once
        cert_paths = [
            '/etc/ssl/certs/ca-certificates.crt',  # Common Linux location
            '/usr/lib/ssl/cert.pem',               # Default SSL path
        ]
        
        cert_path = None
        for path in cert_paths:
            if os.path.exists(path):
                cert_path = path
                break
        
        # Use system default if no cert path found
        if cert_path is None:
            cert_path = True  # Use system default as last resort
        
        for local_file_path in file_list:
            # Check if local file exists
            if not os.path.exists(local_file_path):
                results.append(f"ERROR: File not found: {local_file_path}")
                failed_files.append(local_file_path)
                continue
            
            # Get filename from path
            filename = os.path.basename(local_file_path)
            
            # Construct destination path
            dest_path = upload_path.rstrip('/') + '/' + filename
            
            # Prepare API endpoint
            api_endpoint = f"{filestash_url.rstrip('/')}/api/files/cat"
            params = {
                'path': dest_path,
                'key': api_key,
                'share': share_id
            }
            
            # Attempt upload with retries
            upload_success = False
            last_error = None
            
            # Create a session with proper SSL context (once per file)
            session = requests.Session()
            session.verify = cert_path
            
            for attempt in range(3):
                try:
                    # Add delay between retries (except first attempt)
                    if attempt > 0:
                        time.sleep(1 * attempt)  # 1s, 2s delays
                    
                    with open(local_file_path, 'rb') as file:
                        response = session.post(
                            api_endpoint,
                            params=params,
                            data=file,
                            headers=headers,
                            timeout=30
                        )
                    
                    if response.status_code == 200:
                        results.append(f"SUCCESS: Uploaded {filename} to {dest_path} (attempt {attempt + 1})")
                        upload_success = True
                        break
                    else:
                        last_error = f"HTTP {response.status_code}: {response.text}"
                        
                except requests.RequestException as e:
                    last_error = f"Network error: {str(e)}"
                except Exception as e:
                    last_error = f"Unexpected error: {str(e)}"
            
            if not upload_success:
                error_msg = f"ERROR: Failed to upload {filename} after 3 attempts - {last_error}"
                results.append(error_msg)
                failed_files.append(local_file_path)
        
        # Log failed files if log_file is specified
        if log_file.strip() and failed_files:
            self._log_failed_uploads(log_file.strip(), failed_files)
        
        return ('\n'.join(results),)
    
    def _log_failed_uploads(self, log_file_path: str, failed_files: List[str]):
        """Log failed upload file paths to the specified log file"""
        try:
            # Create parent directories if they don't exist
            log_path = Path(log_file_path)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Append failed files to log
            with open(log_file_path, 'a', encoding='utf-8') as f:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
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
        
        for line in extra_headers.strip().split('\n'):
            line = line.strip()
            if not line or ':' not in line:
                continue
            
            try:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                if key and value:
                    headers[key] = value
            except ValueError:
                # Skip malformed header lines
                continue
        
        return headers
