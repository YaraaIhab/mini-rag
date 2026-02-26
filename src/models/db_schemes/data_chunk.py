from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    _id: Optional[ObjectId]
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0) # chunk_order must be greater than 0
    chunk_project_id: ObjectId



    class Config:
        # to allow ObjectId to be used in the model, this way we can use ObjectId in our models without any issues.
        arbitrary_types_allowed = True 