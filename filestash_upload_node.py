import requests
import os
from typing import List, Tuple, Any


class FilestashUploadNode:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "filenames": ("STRING", {"multiline": True, "default": ""}),
                "filestash_url": ("STRING", {"default": "http://localhost:8334"}),
                "api_key": ("STRING", {"default": ""}),
                "share_id": ("STRING", {"default": ""}),
                "upload_path": ("STRING", {"default": "/uploads/"}),
            }
        }
    
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("upload_results",)
    FUNCTION = "upload_files"
    CATEGORY = "file_operations"

    def upload_files(self, filenames: str, filestash_url: str, api_key: str, share_id: str, upload_path: str) -> Tuple[str]:
        """
        Upload files to Filestash server
        
        Args:
            filenames: Newline-separated list of local file paths
            filestash_url: Base URL of Filestash instance
            api_key: API key for authentication
            share_id: Share ID for the upload location
            upload_path: Destination path on Filestash server
        
        Returns:
            String containing upload results
        """
        if not filenames.strip():
            return ("No filenames provided",)
        
        if not api_key or not share_id:
            return ("API key and Share ID are required",)
        
        file_list = [f.strip() for f in filenames.strip().split('\n') if f.strip()]
        results = []
        
        for local_file_path in file_list:
            try:
                # Check if local file exists
                if not os.path.exists(local_file_path):
                    results.append(f"ERROR: File not found: {local_file_path}")
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
                
                # Read and upload file
                with open(local_file_path, 'rb') as file:
                    response = requests.post(
                        api_endpoint,
                        params=params,
                        data=file,
                        timeout=30
                    )
                
                if response.status_code == 200:
                    results.append(f"SUCCESS: Uploaded {filename} to {dest_path}")
                else:
                    results.append(f"ERROR: Failed to upload {filename} - HTTP {response.status_code}: {response.text}")
                    
            except requests.RequestException as e:
                results.append(f"ERROR: Network error uploading {local_file_path}: {str(e)}")
            except Exception as e:
                results.append(f"ERROR: Unexpected error uploading {local_file_path}: {str(e)}")
        
        return ('\n'.join(results),)


