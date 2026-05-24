from pydantic import BaseModel,Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id") # to allow _id field to be used in the model, this way we can use _id in our models without any issues.
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
    @classmethod
    def get_indexes(cls): #cls is used to access static methods
        return [
            {
                "key": [("project_id", 1)], # 1 for ascending order
                "name": "project_id_index_1",
                "unique": True

            }
        ]

