from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

from sqlalchemy import select, func


class ProjectModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.db_client = db_client

    # -------------------------------------------------
    # FIX: removed async + classmethod (Celery-safe)
    # -------------------------------------------------
    @classmethod
    async def create_instance(cls, db_client: object):
        return cls(db_client)

    # -------------------------------------------------
    # CREATE PROJECT
    # -------------------------------------------------
    async def create_project(self, project: Project):
        """
        Create a project in DB using async SQLAlchemy sessions
        """

        async with self.db_client() as session:
            async with session.begin():
                session.add(project)
            await session.commit()
            await session.refresh(project)
        return project

        with self.db_client() as session:
            with session.begin():
                session.add(project)

            session.commit()
            session.refresh(project)

        return project

    # -------------------------------------------------
    # GET OR CREATE PROJECT
    # -------------------------------------------------
    async def get_or_create_project(self, project_id: str):

        async with self.db_client() as session:
            async with session.begin():
                query = select(Project).where(Project.project_id == project_id)
                result = await session.execute(query)
                project = result.scalar_one_or_none()

                if project is None:
                    project = Project(project_id=project_id)
                    session.add(project)
                    await session.commit()
                    await session.refresh(project)

                return project

    # -------------------------------------------------
    # GET ALL PROJECTS (PAGINATED)
    # -------------------------------------------------
    def get_all_projects(self, page: int = 1, page_size: int = 10):

        with self.db_client() as session:
            with session.begin():

                total_documents = session.execute(
                    select(func.count(Project.project_id))
                ).scalar_one()

                total_pages = total_documents // page_size
                if total_documents % page_size > 0:
                    total_pages += 1

                query = (
                    select(Project)
                    .offset((page - 1) * page_size)
                    .limit(page_size)
                )

                projects = session.execute(query).scalars().all()

                return projects, total_pages