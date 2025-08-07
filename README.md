# ComfyUI-SKCFI-NetworkFileIO

A ComfyUI custom node for uploading files to Filestash servers with robust retry logic and comprehensive configuration options.

## Features

- **Batch file uploads** to Filestash servers via REST API
- **Retry logic** with 3 attempts and progressive backoff delays (1s, 2s)
- **Custom HTTP headers** support for authentication and request customization
- **Failed upload logging** with automatic directory creation
- **Comprehensive error handling** with detailed feedback
- **ComfyUI integration** with proper node structure and UI

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

After installation, you'll find the **"Filestash File Upload"** node under the **"file_operations"** category in ComfyUI.

### Node Parameters

#### Required Inputs:
- **`filenames`** - Newline-separated list of local file paths to upload
- **`filestash_url`** - Base URL of your Filestash instance (e.g., `https://files.example.com`)
- **`api_key`** - API key for Filestash authentication
- **`share_id`** - Share ID for the target upload location
- **`upload_path`** - Destination path on the Filestash server (e.g., `/uploads/`)

#### Optional Inputs:
- **`log_file`** - Path to log failed uploads (creates directories automatically if needed)
- **`extra_headers`** - Custom HTTP headers, one per line in format `Header-Name: value`

#### Output:
- **`upload_results`** - Detailed results string showing success/failure for each file

### Example Usage

```
Filenames:
/path/to/file1.jpg
/path/to/file2.png
/tmp/generated_image.jpg

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
The node implements robust error handling:
- **File validation** - Checks if local files exist before upload
- **3-attempt retry** - Automatic retries with exponential backoff
- **Detailed logging** - Failed uploads logged with timestamps
- **Graceful degradation** - Continues processing remaining files on individual failures

## API Compatibility

This node is designed for Filestash servers and uses the `/api/files/cat` endpoint for uploads. Ensure your Filestash instance supports:
- POST requests to `/api/files/cat`
- Query parameters: `path`, `key`, `share`
- Binary file data in request body

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

### v1.0.0
- Initial release
- Batch file upload functionality
- Retry logic with exponential backoff
- Custom HTTP headers support
- Failed upload logging
- Comprehensive error handling