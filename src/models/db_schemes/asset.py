from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1)
    asset_size: int = Field(ge=0, default=None)
    asset_config: Optional[dict] = Field(default=None)
    asset_pushed_at: datetime = Field(default=datetime.utcnow)

    class Config:
        # to allow ObjectId to be used in the model, this way we can use ObjectId in our models without any issues.
        arbitrary_types_allowed = True

    @classmethod
    def get_indexes(cls):
        # search for assets by project ID and asset name, so we create indexes for these fields to improve query performance
        return[
            {
                "key": [("asset_project_id", 1)], # 1 for ascending order
                "name": "asset_project_id_index_1",
                "unique": False
            },
            {
                "key": [("asset_name", 1),
                        ("asset_project_id", 1)], # 1 for ascending order
                "name": "asset_name_project_id_index_1",
                "unique": True 
            }

        ] 