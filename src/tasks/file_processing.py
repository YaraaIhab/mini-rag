from celery_app import celery_app, setup_celery
from helpers.config import get_settings
import asyncio
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from models.AssetModel import AssetModel
from models.db_schemes import DataChunk
from models import ResponseSignal
from models.enums.AssetTypeEnum import AssetTypeEnum
from controllers import ProcessController
from controllers import NLPController

import logging
logger = logging.getLogger(__name__)

@celery_app.task(name="tasks.file_processing.process_uploaded_file", bind=True, retry_kwargs={'max_retries': 3, 'countdown': 60}) # Retry up to 3 times with a delay of 60 seconds between retries
def process_uploaded_file(self, file_id: int, project_id: int, chunk_size: int, overlap_size: int, do_reset: int):
    
    asyncio.run(_process_uploaded_file(self, file_id, project_id, chunk_size, overlap_size, do_reset))

async def _process_uploaded_file(task_instance, file_id: int, project_id: int, chunk_size: int, overlap_size: int, do_reset: int):
    
    db_engine, vectordb_client = None, None
    try:
        (db_engine, db_client, llm_factory,
        vectordb_provider_factory, generation_client,
        embedding_client, vectordb_client,
        template_parser) = await setup_celery()
        project_model = await ProjectModel.create_instance(db_client=db_client)
        
        project = await project_model.get_or_create_project(project_id=project_id) # Ensure project exists or create it before uploading data to it
        
        nlp_controller = NLPController(vectordb_client=vectordb_client,
                                            generation_client=generation_client,
                                            embedding_client=embedding_client,
                                            template_parser=template_parser,
                                            )

        asset_model = await AssetModel.create_instance(db_client=db_client)

        project_files_ids = {}

        if file_id:
            asset_record = await asset_model.get_asset_record(asset_project_id=project.project_id, asset_name=file_id)
            
            if asset_record is None:
                task_instance.update_state(state='FAILURE', meta={"signal": ResponseSignal.FILE_ID_ERROR.value})
                raise Exception(f"No file found with ID: {file_id}") # Raise an exception to mark the task as failed in Celery with the appropriate error signal
                # return JSONResponse(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "signal": ResponseSignal.FILE_ID_ERROR.value
                #     }
                # )
            project_files_ids = {asset_record.asset_id: asset_record.asset_name}
        else:
            
            project_assets = await asset_model.get_all_project_assets(asset_project_id=project.project_id, asset_type=AssetTypeEnum.FILE.value)
            
            project_files_ids = {
                asset.asset_id: asset.asset_name for asset in project_assets
                }
        
        if len(project_files_ids) == 0:
            task_instance.update_state(state='FAILURE', meta={"signal": ResponseSignal.NO_FILES_TO_PROCESS.value})
            raise Exception("No files to process for this project") # Raise an exception to mark the task as failed in Celery with the appropriate error signal
            
            # return JSONResponse(
            #     status_code=status.HTTP_400_BAD_REQUEST,
            #     content={
            #         "signal": ResponseSignal.NO_FILES_TO_PROCESS.value
            #     }
            # )

        process_controller = ProcessController(project_id=project_id)

        no_records = 0
        processed_files = 0
        chunk_model = await ChunkModel.create_instance(db_client=db_client)

        if(do_reset):
            collection_name = nlp_controller.create_collection_name(project_id = project.project_id)
            _= await nlp_controller.vectordb_client.delete_collection(collection_name=collection_name) # delete the vector db collection to reset it

            _ = await chunk_model.delete_chunks_by_project_id(project_id=project.project_id) # delete associated chunks in the database to reset it


        for asset_id, file_id in project_files_ids.items():
            file_content = process_controller.get_file_content(file_id=file_id)

            if file_content is None:
                logger.error(f"Error while loading file content for file_id: {file_id}") # Error only visible in server logs not returned to client for security 

                continue # skip to the next file if there was an error loading the file content

            file_chunks = process_controller.process_file_content(file_content=file_content,
                                                                file_id=file_id,
                                                                chunk_size=chunk_size,
                                                                overlap_size=overlap_size
                )
            if file_chunks is None or len(file_chunks) == 0:
                logger.error(f"No chunks generated for file_id: {file_id}") # Error only visible in server logs not returned to client for security
                pass
                # return JSONResponse(
                #     status_code=status.HTTP_400_BAD_REQUEST,
                #     content={
                #         "signal": ResponseSignal.PROCESSING_FAILED.value
                #     }
                # )
            file_chunks_records = [
                DataChunk(
                    chunk_text = chunk.page_content,
                    chunk_metadata = chunk.metadata,
                    chunk_order = i+1,
                    chunk_project_id = project.project_id,
                    chunk_asset_id = asset_id
                    )
                for i,chunk in enumerate(file_chunks) # enumerate returns element and its order
            ]
                
            no_records += await chunk_model.insert_many_chunks(chunks=file_chunks_records)
            processed_files += 1

        
        task_instance.update_state(state='SUCCESS', meta={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            }
        )
        return {
                "signal": ResponseSignal.PROCESSING_SUCCESS.value,
                "inserted_chunks": no_records,
                "processed_files": processed_files
            }
    except Exception as e:
        logger.error(f"Error in processing uploaded file: {str(e)}")
        raise e # Re-raise the exception to ensure Celery marks the task as failed
    
    finally:
        try:
            if db_engine:
                await db_engine.dispose()
            
            if vectordb_client:
                await vectordb_client.close()
        except Exception as e:
            logger.error(f"Error while closing resources: {str(e)}")