from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import select, func

class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        #self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]
        self.db_client = db_client

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        # await instance.init_collection() # Ensure the collection is initialized and indexes are created before using the instance
        return instance

    # async def init_collection(self):
    #     all_collections = await self.db_client.list_collection_names()
    #     if DataBaseEnum.COLLECTION_PROJECTS_NAME.value not in all_collections:
    #         self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECTS_NAME.value]
    #         indexes = Project.get_indexes()
    #         for index in indexes:
    #             await self.collection.create_index(index["key"], name=index["name"], unique=index["unique"])

    async def create_project(self, project: Project):
        async with self.db_client() as session: # create a session
            async with session.begin(): #opened the connection
                session.add(project) # added the project
            await session.commit() 
            await session.refresh(project) # check data updated
        
        return project

        # result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True)) # Insert the project data into the collection
        # project.project_id = result.inserted_id # Set the _id field of the project to the inserted ID

        # return project # Return the project with the _id field set


    async def get_or_create_project(self, project_id: str):
        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()
                if project is None:
                    project_rec = Project(
                        project_id = project_id
                    )

                    project = await self.create_project(project=project_rec)
                    return project
                else:
                    return project


        # record = await self.collection.find_one({"project_id": project_id}) # Try to find a project with the given project_id
        # if record is None:
        #     new_project = Project(project_id=project_id) # If not found, create a new project instance
        #     project = await self.create_project(new_project) # Create the project in the database and return it
        #     return project
        # else:
        #     return Project(**record) # convert dict record to Project instance and return it
        

    async def get_all_projects(self, page: int = 1, page_size: int = 10):

        async with self.db_client() as session: # create a session
            async with session.begin(): #opened the connection

                total_documents = await session.execute(select(
                    func.count(Project.project_id)  
                )) # count total number of documents

                total_documents = total_documents.scalar_one() # get the count result

                # calculate total pages
                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = select(Project).offset((page - 1) * page_size).limit(page_size)
                projects = await session.execute(query).scalars().all() # execute the query and get the list of projects

                return projects, total_pages

          
        # # count total number of documents
        # total_documents = await self.collection.count_documents({})

        # # calculate total pages
        # total_pages = total_documents // page_size
        # if total_documents % page_size > 0:
        #     total_pages += 1

        # cursor = self.collection.find({}).skip((page - 1) * page_size).limit(page_size)
        # projects = []
        # async for document in cursor:
        #     projects.append(Project(**document)) # convert dict document to Project instance and add to list

        # return projects, total_pages