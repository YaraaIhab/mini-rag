from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "Successfully validated file"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit"
    FILE_UPLOAD_SUCCESS = "Successfully uploaded file"
    FILE_UPLOAD_FAILED = "Failed to upload file"