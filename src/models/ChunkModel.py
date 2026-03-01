from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection() # Ensure the collection is initialized and indexes are created before using the instance
        return instance

    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value]
            indexes = DataChunk.get_indexes()
            for index in indexes:
                await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])


    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True)) # Insert the chunk data into the collection
        chunk._id = result.inserted_id # Set the _id field of the chunk to the inserted ID
        return chunk # Return the chunk with the _id field 
    
    async def get_chunk(self, chunk_id: str):
        result = await self.collection.find_one(
            {"_id": ObjectId(chunk_id)}
        )

        if result is None:
            return None
        
        return DataChunk(**result) # convert dict result to DataChunk instance and return it

    async def insert_many_chunks(self, chunks: list, batch_size: int=10):
        """Inserts multiple chunks into the database in batches to avoid overwhelming the database.
        It receives a list of DataChunk instances and a batch size.
        It returns the number of chunks inserted."""

        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i+batch_size]

            operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch] 
            await self.collection.bulk_write(operations)
        
        return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):
        """Deletes all chunks associated with a project ID. It receives the project ID and returns the number of chunks deleted."""
        result = await self.collection.delete_many(
            {"chunk_project_id": project_id}
        )
        return result.deleted_count
          
        