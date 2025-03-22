from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    db_uri: str = Field(validation_alias="DB_URI")
    echo_sql: bool = True
    project_name: str = "Movie API"
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
