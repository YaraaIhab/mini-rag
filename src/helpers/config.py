from pydantic_settings import BaseSettings, SettingsConfigDict
#for configuration management, we will use pydantic settings, which is a great way to manage configuration in a clean and organized way, we will create a Settings class that will inherit from BaseSettings, and we will define our configuration variables in that class, and we will use the env_file option to load the configuration from a .env file, this way we can keep our configuration separate from our code, and we can easily change the configuration without changing the code.

class Settings(BaseSettings):
    APP_NAME: str
    APP_VERSION: str

    FILE_ALLOWED_TYPES: list
    FILE_MAX_SIZE: int
    FILE_DEFAULT_CHUNK_SIZE: int


    model_config = SettingsConfigDict(
        env_file=".env"
    )


def get_settings():
    return Settings()
