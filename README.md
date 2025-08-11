# ComfyUI-SKCFI-NetworkFileIO

A ComfyUI custom node package for uploading files to various destinations with robust retry logic and comprehensive configuration options.

## Features

- **Single file uploads** to Filestash servers and generic HTTP endpoints
- **Retry logic** with 3 attempts and progressive backoff delays (1s, 2s)
- **Custom HTTP headers** support for authentication and request customization
- **Failed upload logging** with automatic directory creation
- **Comprehensive error handling** with detailed feedback
- **ComfyUI integration** with proper node structure and UI
- **Status code and response text outputs** for workflow integration

## Installation

### Method 1: ComfyUI Manager (Recommended)
1. Install [ComfyUI Manager](https://github.com/ltdrdata/ComfyUI-Manager)
2. Search for "SKCFI NetworkFileIO" in the manager
3. Click Install and restart ComfyUI

### Method 2: Git Clone
1. Navigate to your ComfyUI custom nodes directory:
   ```bash
   cd ComfyUI/custom_nodes/
   ```
2. Clone this repository:
   ```bash
   git clone https://github.com/your-username/ComfyUI-SKCFI-NetworkFileIO.git
   ```
3. Install dependencies:
   ```bash
   cd ComfyUI-SKCFI-NetworkFileIO
   pip install -r requirements.txt
   ```
4. Restart ComfyUI

### Method 3: Manual Installation
1. Download and extract the repository
2. Copy the entire folder to `ComfyUI/custom_nodes/`
3. Install requirements: `pip install requests>=2.25.0`
4. Restart ComfyUI

## Usage

After installation, you'll find two nodes under the **"file_operations"** category in ComfyUI:
- **"Filestash File Upload"** - Upload to Filestash servers
- **"HTTP File Upload"** - Upload to generic HTTP endpoints

## Filestash File Upload Node

### Parameters

#### Required Inputs:
- **`file_path`** - Path to the single file to upload
- **`filestash_url`** - Base URL of your Filestash instance (e.g., `https://files.example.com`)
- **`api_key`** - API key for Filestash authentication
- **`share_id`** - Share ID for the target upload location
- **`upload_path`** - Destination path on the Filestash server (e.g., `/uploads/`)

#### Optional Inputs:
- **`log_file`** - Path to log failed uploads (creates directories automatically if needed)
- **`extra_headers`** - Custom HTTP headers, one per line in format `Header-Name: value`

#### Outputs:
- **`status_code`** - HTTP status code from the upload response (INT)
- **`result_text`** - Response body or error message (STRING)

## HTTP File Upload Node

### Parameters

#### Required Inputs:
- **`file_path`** - Path to the single file to upload
- **`url`** - Target URL for the HTTP request
- **`method`** - HTTP method (POST or PUT)

#### Optional Inputs:
- **`headers`** - HTTP headers in JSON format or multiline key:value format
- **`timeout`** - Request timeout in seconds (default: 30)

#### Outputs:
- **`status_code`** - HTTP status code from the upload response (INT)
- **`result_text`** - Response body or error message (STRING)

## Example Usage

### Filestash Upload
```
File Path: /tmp/generated_image.jpg
Filestash URL: https://files.myserver.com
API Key: your_api_key_here
Share ID: ABC123
Upload Path: /workflow_outputs/
Log File: /tmp/failed_uploads.log

Extra Headers:
User-Agent: ComfyUI-Workflow/1.0
X-Source: automated-upload
Authorization: Bearer additional_token
```

### HTTP Upload  
```
File Path: /tmp/generated_video.mp4
URL: https://api.example.com/upload
Method: POST
Timeout: 60

Headers (JSON format):
{"Authorization": "Bearer token123", "Content-Type": "video/mp4"}

Headers (key:value format):
Authorization: Bearer token123
User-Agent: ComfyUI-Workflow/1.0
X-Upload-Source: comfyui
```

## Configuration

### Filestash Server Setup
Ensure your Filestash server:
1. Has API access enabled
2. Provides valid API keys for authentication
3. Has appropriate share permissions configured
4. Accepts the file types you plan to upload

### Custom Headers
Use the `extra_headers` parameter for:
- **Authentication**: `Authorization: Bearer token123`
- **User identification**: `User-Agent: MyWorkflow/1.0`
- **Custom metadata**: `X-Source: comfyui-workflow`
- **Content-Type override**: `Content-Type: image/jpeg`

### Error Handling
Both nodes implement robust error handling:
- **File validation** - Checks if local files exist before upload
- **3-attempt retry** - Automatic retries with exponential backoff (1s, 2s delays)
- **Detailed logging** - Failed uploads logged with timestamps (Filestash node only)
- **Status code returns** - HTTP response codes for workflow decision making
- **Comprehensive error messages** - Detailed error information in result_text

## API Compatibility

### Filestash Upload Node
Designed for Filestash servers using the `/api/files/cat` endpoint. Ensure your Filestash instance supports:
- POST requests to `/api/files/cat`
- Query parameters: `path`, `key`, `share`
- Binary file data in request body

### HTTP Upload Node
Generic HTTP upload node that supports:
- POST and PUT methods
- Multipart form-data uploads (field name: `file`)
- Custom headers and timeouts
- Any HTTP endpoint accepting file uploads

## Troubleshooting

### Common Issues

**Files not uploading:**
- Verify Filestash URL, API key, and share ID
- Check file permissions on local files
- Ensure upload path exists on server
- Review Filestash server logs

**Authentication errors:**
- Confirm API key is valid and active
- Check share ID permissions
- Verify extra headers if using additional authentication

**Network timeouts:**
- Default timeout is 30 seconds per attempt
- Large files may need server-side timeout adjustments
- Check network connectivity to Filestash server

**Log file issues:**
- Ensure parent directories are writable
- Check disk space for log file location
- Verify path format is correct for your OS

### Debug Mode
For debugging, check:
1. ComfyUI console output for detailed error messages
2. Log file (if configured) for failed upload paths
3. Filestash server access logs
4. Network connectivity and firewall settings

## Development

### Prerequisites
- Python 3.8+
- ComfyUI installation
- `requests` library

### Testing
1. Update credentials in `test_upload.py`
2. Run: `python test_upload.py`
3. Verify uploads and check results

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make changes with proper testing
4. Submit a pull request

## License

[Add your license information here]

## Support

For issues and questions:
- GitHub Issues: [Repository Issues Page]
- ComfyUI Community: [ComfyUI Discord/Forums]

## Changelog

### v2.0.0
- **BREAKING**: Changed to single file upload per node for better workflow control
- **BREAKING**: Updated return types to (status_code, result_text) instead of upload_results string
- Added new HTTP File Upload node for generic endpoints
- Both nodes now return consistent status_code and result_text outputs
- Maintained retry logic and error handling
- Updated documentation and examples

### v1.0.0
- Initial release
- Batch file upload functionality (deprecated in v2.0.0)
- Retry logic with exponential backoff
- Custom HTTP headers support
- Failed upload logging
- Comprehensive error handling