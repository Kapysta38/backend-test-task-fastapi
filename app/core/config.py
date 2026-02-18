from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend Test Task FastAPI"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: Literal["dev", "test", "prod"] = "dev"

    DOCS_URL_PATH: str = "/api/docs"
    REDOC_URL_PATH: str = "/api/redoc"
    API_VERSION: str = "v1"


settings = Settings()
