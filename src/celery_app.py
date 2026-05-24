from celery import Celery
from helpers.config import get_settings
from stores.llm.LLMProviderFactory import LLMProviderFactory
from stores.vectordb.VectorDBProviderFactory import VectorDBProviderFactory
from stores.llm.templates.template_parser import TemplateParser
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

settings = get_settings()

async def setup_celery():
    settings = get_settings()

    # app.mongo_conn = AsyncIOMotorClient(settings.MONGODB_URI)
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"
    db_engine = create_async_engine(postgres_conn) # to create session 
    db_client = sessionmaker(
        db_engine, class_= AsyncSession, expire_on_commit=False
    )
    # app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    lmm_factory = LLMProviderFactory(config=settings)
    vectordb_provider_factory = VectorDBProviderFactory(config=settings, db_client=db_client)

    # generation client
    generation_client = lmm_factory.create(provider = settings.GENERATION_BACKEND)
    generation_client.set_generation_model(settings.GENERATION_MODEL_ID)

    # embedding client
    embedding_client = lmm_factory.create(provider = settings.EMBEDDING_BACKEND)
    embedding_client.set_embedding_model(model_id = settings.EMBEDDING_MODEL_ID,
                                          embedding_size = settings.EMBEDDING_MODEL_SIZE)

    # vectordb client
    vectordb_client = vectordb_provider_factory.create(provider = settings.VECTOR_DB_BACKEND)
    await vectordb_client.connect()

    # template parser
    template_parser = TemplateParser(language=settings.PRIMARY_LANG, default_language=settings.DEFAULT_LANG,)
    return (
        db_engine,
        db_client,
        lmm_factory,
        vectordb_provider_factory,
        generation_client,
        embedding_client,
        vectordb_client,
        template_parser
    )

# create celery app instance
celery_app = Celery(
    "minirag",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["tasks.mail_service", "tasks.file_processing"] # Include the module where your tasks are defined, so Celery can discover them
)

# Optional: Configure additional Celery settings

celery_app.conf.update(
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],
    
    # Timw limits - prevents tasks from running indefinitely
    task_time_limit=settings.CELERY_TASK_TIME_LIMIT,
    
    # Task safety - late acknowledgment prevents task loss on worker crash
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,
    
    task_ignore_result=False,  # Set to True if you don't need task results stored
    
    result_expires=3600,  # Expire results after 1 hour (adjust as needed)
    
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,

    # Connection settings for better reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

    task_routes={
        "tasks.mail_service.send_email_report": {"queue": "mail_server_queue"},
        "tasks.file_processing.process_uploaded_file": {"queue": "file_processing_queue"},
    } # Route the send_email_report task to a specific queue for better organization and scalability

)

celery_app.conf.task_default_queue = "default"