from .filestash_upload_node import FilestashUploadNode

NODE_CLASS_MAPPINGS = {
    "FilestashUploadNode": FilestashUploadNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "FilestashUploadNode": "Filestash File Upload"
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]