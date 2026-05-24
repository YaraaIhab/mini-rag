from urllib import request

from fastapi import FastAPI, APIRouter, Depends, UploadFile, status, Request
from fastapi.responses import JSONResponse
from routes.schemes.nlp import PushRequest, SearchRequest
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
from controllers import NLPController
from models import ResponseSignal
from tqdm.auto import tqdm

import logging

logger = logging.getLogger('uvicorn.error')

nlp_router = APIRouter(
    prefix="/api/v1/nlp",
    tags=["api_v1", "nlp"],
)

@nlp_router.post("/index/push/{project_id}")
async def index_project(request: Request, project_id: int, push_request: PushRequest):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)
    chunk_model = await ChunkModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id) # Ensure project exists or create it before pushing data to it
    
    if not project:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.PROJECT_NOT_FOUND_ERROR.value})
    
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   template_parser=request.app.template_parser
                                   )
    
    has_records = True
    page_no = 1
    inserted_items_count = 0
    idx = 0

    # create collection if not exists
    collection_name = nlp_controller.create_collection_name(project_id = project.project_id)

    _ = await nlp_controller.vectordb_client.create_collection(collection_name=collection_name,
                                                               embedding_size=nlp_controller.embedding_client.embedding_size,
                                                               do_reset=push_request.do_reset)
    
    # setup batch processing to avoid memory issues when indexing large number of chunks, we will process the chunks in batches of 1000 chunks and insert them into the vector db collection, we will repeat this process until we have processed all the chunks in the database for the project
    total_chunks_count = await chunk_model.get_total_chunks_count_by_project_id(project_id=project.project_id)
    pbar = tqdm(total=total_chunks_count, desc="Indexing chunks into vector db collection",position=0, unit="chunk")

    while has_records:
        page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_no=page_no)
        
        if len(page_chunks):
            page_no +=1

        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break

        chunks_ids = [chunk.chunk_id for chunk in page_chunks]
        idx += len(page_chunks)

        is_inserted = await nlp_controller.index_into_vector_db(project=project, chunks=page_chunks, chunks_ids=chunks_ids) # reset the vector db collection only for the first batch of chunks to avoid deleting the indexed chunks in the next batches
        
        if not is_inserted:
            return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                                content={"signal": ResponseSignal.VECTOR_DB_INDEXING_ERROR.value})
        
        pbar.update(len(page_chunks))
        inserted_items_count += len(page_chunks)

    return JSONResponse(status_code=status.HTTP_200_OK,
                         content={"signal": ResponseSignal.VECTOR_DB_INDEXING_SUCCESS.value, 
                                  "inserted_chunks_count": inserted_items_count})
    

@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(request: Request, project_id: int):

    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id) # Ensure project exists or create it before pushing data to it
    
   
    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   template_parser=request.app.template_parser
                                   )
    
    collection_info = await nlp_controller.get_vector_db_collection_info(project=project)
    #print(collection_info)

    return JSONResponse(status_code=status.HTTP_200_OK,
                         content={"signal": ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value, 
                                  "collection_info": collection_info})

@nlp_router.post("/index/search/{project_id}")
async def search_index(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id) # Ensure project exists or create it before pushing data to it

    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   template_parser=request.app.template_parser)


    results = await nlp_controller.search_vector_db_collection(
        project=project, query=search_request.query, limit=search_request.limit
    )
   
    if not results:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.VECTORDB_SEARCH_ERROR.value})
    
    return JSONResponse(content={"signal": ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
                                "results": [r.model_dump() for r in results]})

@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(db_client=request.app.db_client)

    project = await project_model.get_or_create_project(project_id=project_id) # Ensure project exists or create it before pushing data to it

    nlp_controller = NLPController(vectordb_client=request.app.vectordb_client,
                                   generation_client=request.app.generation_client,
                                   embedding_client=request.app.embedding_client,
                                   template_parser=request.app.template_parser)
    
    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(
        project=project, query=search_request.query, limit=search_request.limit)
    
    if not answer:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"signal": ResponseSignal.RAG_RESPONSE_ERROR.value})
    
    return JSONResponse(content={"signal": ResponseSignal.RAG_RESPONSE_SUCCESS.value,
                                "answer": answer,
                                "full_prompt": full_prompt,
                                "chat_history": chat_history,
                                })

