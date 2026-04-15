from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    chunk_text: str = Field(..., min_length=1)
    chunk_metadata: dict
    chunk_order: int = Field(..., gt=0)
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId

    class Config:
        # to allow ObjectId to be used in the model, this way we can use ObjectId in our models without any issues.
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        return[
            {
                "key": [("chunk_project_id", 1)], # 1 for ascending order
                "name": "chunk_project_id_index_1",
                "unique": False
            }

        ]

class RetrievedDocument(BaseModel):
    # schema for retrived documents from the db (3ashan matala3sh kol el output el tale3 w atala3 el text wl score bas)
    text: str
    score: float