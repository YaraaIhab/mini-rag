from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List
import json

class NLPController(BaseController):

    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()
        
        self.vectordb_client = vectordb_client
        self.generation_client = generation_client
        self.embedding_client = embedding_client
        self.template_parser = template_parser

    def create_collection_name(self, project_id: str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip() #strip to remove any leading/trailing whitespace
    
    async def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id = project.project_id)
        return await self.vectordb_client.delete_collection(collection_name = collection_name)
    
    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id = project.project_id)
        collection_info = await self.vectordb_client.get_collection_info(collection_name = collection_name)
        
        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__) # convert any non-serializable objects to dictionaries
        )       
    
    async def index_into_vector_db(self, project: Project,chunks:List[DataChunk],chunks_ids: List[int], do_reset: bool = False):
        # step 1: get collection name
        collection_name = self.create_collection_name(project_id = project.project_id)

        # step 2: manage items
        texts = [chunk.chunk_text for chunk in chunks]
        metadatas = [chunk.chunk_metadata for chunk in chunks]
        vectors = self.embedding_client.embed_text(input_text=texts, document_type=DocumentTypeEnum.DOCUMENT.value)
        
        # step 3: create collection if not exists
        _ = await self.vectordb_client.create_collection(collection_name=collection_name, embedding_size=self.embedding_client.embedding_size)
        
        # step 4: insert into vector db
        _ = await self.vectordb_client.insert_many(collection_name=collection_name, texts=texts, vectors=vectors, 
                    metadata=metadatas, record_ids=chunks_ids)
        
        return True
    
    async def search_vector_db_collection(self, project: Project, query: str, limit: int = 10):
        # step 1: get collection name
        query_vector = None
        collection_name = self.create_collection_name(project_id = project.project_id)

        # step 2: get text embedding vector
        vectors = self.embedding_client.embed_text(input_text=query, document_type=DocumentTypeEnum.QUERY.value)
        
        if not vectors or len(vectors) == 0:
            return False
        
        if isinstance(vectors, list) and len(vectors) > 0:
            query_vector = vectors[0] # in case the embedding client returns a list of vectors, we take the first one since we are only embedding one query at a time
        
        if not query_vector:
            return False

        # step 3: do semantic search in the vector db collection and return the results
        results = await self.vectordb_client.search_by_vector(collection_name=collection_name, vector=query_vector, limit=limit)
        
        if not results:
            return False

        return results
    
    async def answer_rag_question(self, project: Project, query: str, limit: int=10):
        
        answer, full_prompt, chat_history = None, None, None

        # step 1: retrieve related documents
        retrieved_documents = await self.search_vector_db_collection(
            project=project,
            query=query,
            limit=limit, 
        )

        if not retrieved_documents or len(retrieved_documents) == 0:
            return answer, full_prompt, chat_history
        
        # step 2: construct system prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")

        document_prompt = "\n".join([
            self.template_parser.get("rag", "document_prompt",
                                    {"doc_num": idx + 1,
                                     "chunk_text": self.generation_client.process_text(doc.text),
                                     })
            for idx, doc in enumerate(retrieved_documents)   
        ])

        footer_prompt = self.template_parser.get(
            "rag",
            "footer_prompt",
            vars={"query": query}
        )
    

        chat_history = [
            self.generation_client.construct_prompt(prompt=system_prompt, role=self.generation_client.enums.SYSTEM.value),
        ]

        full_prompt = "\n\n".join([document_prompt, footer_prompt])

        answer = self.generation_client.generate_response(prompt=full_prompt, chat_history=chat_history)

        return answer, full_prompt, chat_history