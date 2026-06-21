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
    PROJECT_NOT_FOUND_ERROR = "Project not found"
    VECTOR_DB_INDEXING_ERROR = "Error while indexing into vector db"
    VECTOR_DB_INDEXING_SUCCESS = "Successfully indexed into vector db"
    VECTORDB_COLLECTION_RETRIEVED = "Successfully retrieved vector db collection info"
    VECTORDB_SEARCH_ERROR = "Error while searching in vector db collection"
    VECTORDB_SEARCH_SUCCESS = "Successfully searched in vector db collection"
    RAG_RESPONSE_SUCCESS = "Successfully generated response for RAG question"
    RAG_RESPONSE_ERROR = "Error while generating response for RAG question"
    DATA_PUSH_TASK_READY = "Data push task has been created and is being processed"
    PROCESS_AND_PUSH_WORKFLOW_TASK_READY = "Process and push workflow task has been created and is being processed"
