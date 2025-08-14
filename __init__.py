from .filestash_upload_node import FilestashUploadNode
from .http_upload_node import HttpUploadNode
from .multipart_file_http_upload_node import MultipartFileHTTPUploadNode

NODE_CLASS_MAPPINGS = {
    "FilestashUploadNode": FilestashUploadNode,
    "HttpUploadNode": HttpUploadNode,
    "MultipartFileHTTPUploadNode": MultipartFileHTTPUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilestashUploadNode": "Filestash File Upload",
    "HttpUploadNode": "HTTP File Upload",
    "MultipartFileHTTPUploadNode": "Multipart File HTTP Upload"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]