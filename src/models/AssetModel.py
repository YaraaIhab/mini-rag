from .BaseDataModel import BaseDataModel
from .db_schemes import Asset
from .enums.DataBaseEnum import DataBaseEnum
from bson import ObjectId

class AssetModel(BaseDataModel):
    
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]
    
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection() # Ensure the collection is initialized and indexes are created before using the instance
        return instance
    
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_ASSETS_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_ASSETS_NAME.value]
            indexes = Asset.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_asset(self, asset: Asset):

        result = await self.collection.insert_one(asset.dict(by_alias=True, exclude_unset=True)) # Insert the asset data into the collection
        asset.id = result.inserted_id # Set the _id field of the asset to the inserted ID

        return asset # Return the asset with the _id field set
    
    async def get_all_project_assets(self, asset_project_id: str, asset_type: str):
        records =  await self.collection.find({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_type": asset_type
        }).to_list(length=None) # Find all assets with the given project ID and asset type
        return [
            Asset(**record) for record in records # convert dict record to Asset instance and return list of assets
        ]
    
    async def get_asset_record(self, asset_project_id: str, asset_name: str):
        record = await self.collection.find_one({
            "asset_project_id": ObjectId(asset_project_id) if isinstance(asset_project_id, str) else asset_project_id,
            "asset_name": asset_name
        }) # Find the asset with the given project ID and asset name
        
        if record:
            return Asset(**record) # convert dict record to Asset instance and return it
        
        return None
    
