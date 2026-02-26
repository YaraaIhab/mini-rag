from pydantic import BaseModel,Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    _id: Optional[ObjectId] 
    project_id: str = Field(..., min_length=1)

    @validator('project_id')
    def validate_project_id(cls, value):
        # validate user input (value)
        if not value.isalnum():
            raise ValueError('project_id must be alphanumeric')
        return value
    
    class Config:
        # to allow ObjectId to be used in the model, this way we can use ObjectId in our models without any issues.
        arbitrary_types_allowed = True

