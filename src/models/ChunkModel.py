from ast import stmt
from unittest import result

from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, func, delete
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        #self.collection = self.db_client[DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value]
        self.db_client = db_client
        
    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        #await instance.init_collection() # Ensure the collection is initialized and indexes are created before using the instance
        return instance

    # async def init_collection(self):
    #     all_collections = await self.db_client.list_collection_names()
    #     if DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value not in all_collections:
    #         self.collection = self.db_client[DataBaseEnum.COLLECTION_DATA_CHUNKS_NAME.value]
    #         indexes = DataChunk.get_indexes()
    #         for index in indexes:
    #             await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])


    async def create_chunk(self, chunk: DataChunk):
        async with self.db_client() as session: # create a session
            async with session.begin(): #opened the connection
                session.add(chunk) # added the chunk
            await session.commit() 
            await session.refresh(chunk) # check data updated
        return chunk



        # result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True)) # Insert the chunk data into the collection
        # chunk._id = result.inserted_id # Set the _id field of the chunk to the inserted ID
        # return chunk # Return the chunk with the _id field 
    
    async def get_chunk(self, chunk_id: str):

        async with self.db_client() as session: # create a session
            result = await session.execute(select(DataChunk).where(DataChunk.chunk_id == chunk_id)) # create a query to find the chunk by chunk_id
            chunk = result.scalar_one_or_none() # execute the query and get the result (check if there is minimum one chunk)
            return chunk
        

        # result = await self.collection.find_one(
        #     {"_id": ObjectId(chunk_id)}
        # )

        # if result is None:
        #     return None
        
        # return DataChunk(**result) # convert dict result to DataChunk instance and return it

    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        async with self.db_client() as session:
                    async with session.begin():
                        for i in range(0, len(chunks), batch_size):
                            batch = chunks[i:i+batch_size]
                            session.add_all(batch)
                    await session.commit()
        return len(chunks)

    #     """Inserts multiple chunks into the database in batches to avoid overwhelming the database.
    #     It receives a list of DataChunk instances and a batch size.
    #     It returns the number of chunks inserted."""

    #     for i in range(0, len(chunks), batch_size):
    #         batch = chunks[i:i+batch_size]

    #         operations = [InsertOne(chunk.dict(by_alias=True, exclude_unset=True)) for chunk in batch] 
    #         await self.collection.bulk_write(operations)
        
    #     return len(chunks)
    
    async def delete_chunks_by_project_id(self, project_id: ObjectId):

        async with self.db_client() as session:
            stmt = delete(DataChunk).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(stmt)
            await session.commit()
        return result.rowcount

        # """Deletes all chunks associated with a project ID. It receives the project ID and returns the number of chunks deleted."""
        # result = await self.collection.delete_many(
        #     {"chunk_project_id": project_id}
        # )
        # return result.deleted_count
    
    async def get_project_chunks(self, project_id: ObjectId, page_no: int = 1, page_size: int = 50):
         
        async with self.db_client() as session:
            stmt = select(DataChunk).where(DataChunk.chunk_project_id == project_id).offset((page_no - 1) * page_size).limit(page_size)
            result = await session.execute(stmt)
            records = result.scalars().all()
        return records

    #   records = await self.collection.find(
    #       {"chunk_project_id": project_id}
    #   ).skip((page_no - 1) * page_size).limit(page_size).to_list(length=None)

    #   return [DataChunk(**chunk) for chunk in records]

    async def get_total_chunks_count_by_project_id(self, project_id: ObjectId):
        total_count = 0
        async with self.db_client() as session:
            count_sql = select(func.count(DataChunk.chunk_id)).where(DataChunk.chunk_project_id == project_id)
            result = await session.execute(count_sql)
            total_count = result.scalar()
        
        return total_count

        # """Returns the total number of chunks associated with a project ID. It receives the project ID and returns the count."""
        # count = await self.collection.count_documents(
        #     {"chunk_project_id": project_id}
        # )
        # return count