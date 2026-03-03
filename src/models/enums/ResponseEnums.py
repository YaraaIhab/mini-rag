from enum import Enum

class ResponseSignal(Enum):

    FILE_VALIDATED_SUCCESS = "Successfully validated file"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeds the maximum limit"
    FILE_UPLOAD_SUCCESS = "Successfully uploaded file"
    FILE_UPLOAD_FAILED = "Failed to upload file"
    PROCESSING_FAILED = "Failed to process file"
    PROCESSING_SUCCESS = "Successfully processed file"
    NO_FILES_TO_PROCESS = "No files to process"
    FILE_ID_ERROR = "No file found with this ID"