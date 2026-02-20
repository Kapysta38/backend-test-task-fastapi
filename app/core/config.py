from anyio.functools import lru_cache
from pydantic import EmailStr, computed_field
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings

from app.core.constants import Environment


class Settings(BaseSettings):
    PROJECT_NAME: str = "Backend Test Task FastAPI"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENV: Environment = Environment.DEV

    DOCS_URL_PATH: str = "/api/docs"
    REDOC_URL_PATH: str = "/api/redoc"
    API_VERSION: str = "v1"

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "changethis"
    POSTGRES_DB: str = "db"

    SECRET_KEY: str = "changethis"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    FIRST_SUPERUSER: EmailStr = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "changethis"

    ALLOWED_TAGS: list[str] = [
        "p",
        "br",
        "strong",
        "em",
        "ul",
        "ol",
        "li",
        "a",
        "h1",
        "h2",
        "h3",
        "h4",
        "blockquote",
        "code",
        "pre",
    ]
    ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
        "a": ["href", "title"],
        "img": ["alt"],
    }

    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"

    MAX_REQUESTS_PER_MINUTE: int = 60

    @computed_field(return_type=str)
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return str(
            MultiHostUrl.build(
                scheme="postgresql+psycopg",
                username=self.POSTGRES_USER,
                password=self.POSTGRES_PASSWORD,
                host=self.POSTGRES_SERVER,
                port=self.POSTGRES_PORT,
                path=self.POSTGRES_DB,
            )
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
