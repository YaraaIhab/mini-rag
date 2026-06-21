from pydantic import BaseModel, Field
from typing import Optional

class ProcessRequest(BaseModel):
    """Request schema for file processing tasks.
    
    file_id: Optional ID of specific file to process. If None, all project files are processed.
    chunk_size: Size of text chunks for splitting (bytes).
    overlap_size: Overlap between consecutive chunks (bytes).
    do_reset: Whether to reset vector collections and chunk data before processing.
    """
    file_id: Optional[int] = Field(None, description="File ID to process, or None for all files")
    chunk_size: int = Field(default=100, ge=1, description="Chunk size in bytes")
    overlap_size: int = Field(default=20, ge=0, description="Chunk overlap in bytes")
    do_reset: bool = Field(default=False, description="Reset vector DB before processing")
     

