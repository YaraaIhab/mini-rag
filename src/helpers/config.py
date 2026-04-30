from pydantic_settings import BaseSettings, SettingsConfigDict
#for configuration management, we will use pydantic settings, which is a great way to manage configuration in a clean and organized way, we will create a Settings class that will inherit from BaseSettings, and we will define our configuration variables in that class, and we will use the env_file option to load the configuration from a .env file, this way we can keep our configuration separate from our code, and we can easily change the configuration without changing the code.
from typing import List

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int

    # MONGODB_URI: str
    # MONGODB_DATABASE: str

    POSTGRES_USERNAME: str
    POSTGRES_PASSWORD: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_MAIN_DATABASE: str

    GENERATION_BACKEND: str 
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: str = None
    OPENAI_API_URL: str = None

    COHERE_API_KEY: str = None

    GENERATION_MODEL_ID_LITERALS: List[str] = None
    GENERATION_MODEL_ID: str = None
    EMBEDDING_MODEL_ID: str = None
    EMBEDDING_MODEL_SIZE: int = None

    DEFAULT_INPUT_MAX_CHARACTERS: int = None
    DEFAULT_OUTPUT_MAX_TOKENS: int = None
    DEFAULT_TEMPERATURE: float = None

    VECTOR_DB_BACKEND_LITERALS: List[str] = None
    VECTOR_DB_BACKEND: str
    VECTOR_DB_PATH: str
    VECTOR_DB_DISTANCE_METHOD: str = None
    VECTOR_DB_PGVECTOR_INDEX_THRESHOLD: int = 100

    DEFAULT_LANG: str = "en"
    PRIMARY_LANG: str = "en"


    model_config = SettingsConfigDict(
        env_file=".env"
    )


def get_settings():
    return Settings()
