# ComfyUI Filestash Upload Node

## Project Overview
This is a ComfyUI custom node that enables uploading files to a Filestash server directly from ComfyUI workflows. The node provides robust upload functionality with retry logic and failure logging capabilities.

## Project Structure
- `__init__.py` - Module initialization and node registration for ComfyUI
- `filestash_upload_node.py` - Main node implementation with upload logic
- `requirements.txt` - Python dependencies (requests>=2.25.0)
- `pyproject.toml` - Modern Python packaging metadata
- `test_upload.py` - Test script for development/debugging
- `.gitignore` - Standard Python gitignore patterns

## Key Features
- **Batch file uploads** to Filestash server via API
- **3-attempt retry logic** with progressive backoff delays (1s, 2s)
- **Optional failure logging** - logs failed file paths with timestamps
- **Auto-directory creation** for log files
- **Input validation** for required parameters
- **Error handling** with detailed error messages

## Node Interface
**Required inputs:**
- `filenames` - Newline-separated list of local file paths to upload
- `filestash_url` - Base URL of the Filestash instance
- `api_key` - API key for authentication
- `share_id` - Share ID for the upload location  
- `upload_path` - Destination path on Filestash server

**Optional inputs:**
- `log_file` - Path to log failed uploads (creates directories if needed)

**Output:**
- `upload_results` - String containing detailed upload results for each file

## Installation
1. Copy the entire directory to ComfyUI's `custom_nodes/` folder
2. ComfyUI will automatically install dependencies from `requirements.txt`
3. Restart ComfyUI to load the new node

## Development Notes
- Uses ComfyUI's standard node structure with proper `INPUT_TYPES`, `RETURN_TYPES`, etc.
- Follows Python best practices with type hints and comprehensive error handling
- Test script available for development - update credentials in `test_upload.py` before running
- Node appears in ComfyUI under "file_operations" category as "Filestash File Upload"

## Testing
Run `python test_upload.py` after updating the test credentials to verify functionality.

## Dependencies
- `requests>=2.25.0` for HTTP API calls
- `pathlib` for cross-platform path handling (built-in Python 3.4+)
- Standard library modules: `os`, `time`, `typing`