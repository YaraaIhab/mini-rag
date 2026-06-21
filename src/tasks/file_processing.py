from celery_app import celery_app, setup_celery
from helpers.config import get_settings
import asyncio
import inspect
import logging

from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk
from models import ResponseSignal
from models.enums.AssetTypeEnum import AssetTypeEnum

from controllers import ProcessController
from controllers import NLPController
from utils.idempotency_manager import IdempotencyManager

logger = logging.getLogger(__name__)


# ----------------------------
# CLEANUP
# ----------------------------
async def _cleanup_celery_resources(db_engine, vectordb_client):
    if db_engine:
        db_engine.dispose()

    if vectordb_client:
        close_fn = getattr(vectordb_client, "disconnect", None) or getattr(vectordb_client, "close", None)
        if close_fn:
            if inspect.iscoroutinefunction(close_fn):
                await close_fn()
            else:
                close_fn()


# ----------------------------
# CELERY ENTRY
# ----------------------------
@celery_app.task(
    name="tasks.file_processing.process_uploaded_file",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 3, 'countdown': 60}
)
def process_uploaded_file(
    self,
    file_id: int,        
    project_id: int,
    chunk_size: int,
    overlap_size: int,
    do_reset: int
):
    return asyncio.run(
        _process_uploaded_file(
            self,
            file_id,
            project_id,
            chunk_size,
            overlap_size,
            do_reset
        )
    )


# ----------------------------
# CORE LOGIC
# ----------------------------
async def _process_uploaded_file(
    task_instance,
    file_id: int,
    project_id: int,
    chunk_size: int,
    overlap_size: int,
    do_reset: int
):

    db_engine, vectordb_client = None, None

    try:
        (
            db_engine, db_client,
            llm_factory,
            vectordb_provider_factory,
            generation_client,
            embedding_client,
            vectordb_client,
            template_parser
        ) = await setup_celery()

        # ----------------------------
        # IDEMPOTENCY
        # ----------------------------
        idempotency_manager = IdempotencyManager(db_client=db_client, db_engine=db_engine)

        task_args = {
            "project_id": project_id,
            "file_id": file_id,
            "chunk_size": chunk_size,
            "overlap_size": overlap_size,
            "do_reset": do_reset
        }

        task_name = "tasks.file_processing.process_uploaded_file"
        settings = get_settings()

        should_execute, existing_task = await idempotency_manager.should_execute_task(
            task_name=task_name,
            task_args=task_args,
            celery_task_id=task_instance.request.id,
            task_time_limit=settings.CELERY_TASK_TIME_LIMIT
        )

        if not should_execute:
            logger.warning(f"Cannot handle task | status: {existing_task.status}")
            return existing_task.result

        if existing_task:
            await idempotency_manager.update_task_status(
                execution_id=existing_task.execution_id,
                status='PENDING'
            )
            task_record = existing_task
        else:
            task_record = await idempotency_manager.create_task_record(
                task_name=task_name,
                task_args=task_args,
                celery_task_id=task_instance.request.id
            )

        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='STARTED'
        )

        # ----------------------------
        # PROJECT
        # ----------------------------
        project_model = await ProjectModel.create_instance(db_client=db_client)
        project = await project_model.get_or_create_project(project_id=project_id)

        # ----------------------------
        # NLP CONTROLLER
        # ----------------------------
        nlp_controller = NLPController(
            vectordb_client=vectordb_client,
            generation_client=generation_client,
            embedding_client=embedding_client,
            template_parser=template_parser,
        )

        # ----------------------------
        # ASSETS
        # ----------------------------
        asset_model = await AssetModel.create_instance(db_client=db_client)

        project_files_ids = {}

        if file_id:
            asset_record = await asset_model.get_asset_record(
                asset_project_id=project.project_id,
                asset_name=file_id
            )

            if asset_record is None:
                task_instance.update_state(
                    state='FAILURE',
                    meta={"signal": ResponseSignal.FILE_ID_ERROR.value}
                )

                await idempotency_manager.update_task_status(
                    execution_id=task_record.execution_id,
                    status='FAILURE',
                    result={"signal": ResponseSignal.FILE_ID_ERROR.value}
                )

                raise Exception(f"No file found with ID: {file_id}")

            project_files_ids = {asset_record.asset_id: asset_record.asset_name}

        else:
            project_assets = await asset_model.get_all_project_assets(
                asset_project_id=project.project_id,
                asset_type=AssetTypeEnum.FILE.value
            )

            project_files_ids = {
                a.asset_id: a.asset_name for a in project_assets
            }

        if len(project_files_ids) == 0:
            task_instance.update_state(
                state='FAILURE',
                meta={"signal": ResponseSignal.NO_FILES_TO_PROCESS.value}
            )

            await idempotency_manager.update_task_status(
                execution_id=task_record.execution_id,
                status='FAILURE',
                result={"signal": ResponseSignal.NO_FILES_TO_PROCESS.value}
            )

            raise Exception("No files found for project")

        # ----------------------------
        # PROCESSING
        # ----------------------------
        process_controller = ProcessController(project_id=project_id)

        chunk_model = await ChunkModel.create_instance(db_client=db_client)

        no_records = 0
        processed_files = 0

        # RESET
        if do_reset == 1:
            collection_name = nlp_controller.create_collection_name(project_id=project.project_id)

            await vectordb_client.delete_collection(collection_name=collection_name)

            await chunk_model.delete_chunks_by_project_id(
                project_id=project.project_id
            )

        # ----------------------------
        # CHUNK LOOP
        # ----------------------------
        for asset_id, file_id in project_files_ids.items():

            file_content = process_controller.get_file_content(file_id=file_id)

            if file_content is None:
                logger.error(f"Missing file content: {file_id}")
                continue

            file_chunks = process_controller.process_file_content(
                file_content=file_content,
                file_id=file_id,
                chunk_size=chunk_size,
                overlap_size=overlap_size
            )

            if not file_chunks:
                logger.error(f"No chunks generated: {file_id}")
                continue

            records = [
                DataChunk(
                    chunk_text=c.page_content,
                    chunk_metadata=c.metadata,
                    chunk_order=i + 1,
                    chunk_project_id=project.project_id,
                    chunk_asset_id=asset_id
                )
                for i, c in enumerate(file_chunks)
            ]

            no_records += await chunk_model.insert_many_chunks(records)
            processed_files += 1

        # ----------------------------
        # SUCCESS
        # ----------------------------
        task_instance.update_state(
            state='SUCCESS',
            meta={"signal": ResponseSignal.PROCESSING_SUCCESS.value}
        )

        await idempotency_manager.update_task_status(
            execution_id=task_record.execution_id,
            status='SUCCESS',
            result={"signal": ResponseSignal.PROCESSING_SUCCESS.value}
        )

        return {
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records,
            "processed_files": processed_files,
            "project_id": project_id,
            "do_reset": do_reset
        }

    except Exception as e:
        logger.error(f"Error in processing uploaded file: {str(e)}")
        raise

    finally:
        try:
            await _cleanup_celery_resources(db_engine, vectordb_client)
        except Exception as e:
            logger.error(f"Error while closing resources: {str(e)}")