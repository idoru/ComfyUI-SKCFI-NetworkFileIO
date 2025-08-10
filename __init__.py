from .filestash_upload_node import FilestashUploadNode
from .http_upload_node import HttpUploadNode

NODE_CLASS_MAPPINGS = {
    "FilestashUploadNode": FilestashUploadNode,
    "HttpUploadNode": HttpUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilestashUploadNode": "Filestash File Upload",
    "HttpUploadNode": "HTTP File Upload"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]