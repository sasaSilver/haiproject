from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_uri: str
    echo_sql: bool = False
    project_name: str = "Movie Recommendations API"
    secret: str
    algorithm: str
    access_token_expire_m: int
    model_config = SettingsConfigDict(
        env_file=".env"
    )

settings = Settings()
