from pydantic import PostgresDsn, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_uri_pg: PostgresDsn = Field(validation_alias="DB_URI") # get db_uri from "DB_URI" env var
    db_uri: str = None
    echo_sql: bool = True
    project_name: str = "POZZED UP API"
    model_config = SettingsConfigDict(env_file="../../.env")
    
    @property
    def db_uri(self) -> str:
        return str(self.db_uri_pg)

settings = Settings()
