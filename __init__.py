from .filestash_upload_node import FilestashUploadNode
from .http_upload_node import HttpUploadNode
from .multipart_video_files_http_node import MultipartVideoFilesHTTPRequestNode

NODE_CLASS_MAPPINGS = {
    "FilestashUploadNode": FilestashUploadNode,
    "HttpUploadNode": HttpUploadNode,
    "MultipartVideoFilesHTTPRequestNode": MultipartVideoFilesHTTPRequestNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilestashUploadNode": "Filestash File Upload",
    "HttpUploadNode": "HTTP File Upload",
    "MultipartVideoFilesHTTPRequestNode": "Multipart Video Files HTTP Request"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]