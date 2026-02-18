from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from app.api.v1.router import router as api_router
from app.core.config import get_settings
from app.db.session import initialize_database


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    # startup
    await initialize_database()
    yield
    # shutdown


settings = get_settings()
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    root_path=f"/api/{settings.API_VERSION}",
    docs_url=settings.DOCS_URL_PATH,
    redoc_url=settings.REDOC_URL_PATH,
    lifespan=lifespan,
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
