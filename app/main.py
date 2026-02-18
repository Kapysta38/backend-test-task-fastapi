import uvicorn
from fastapi import FastAPI

from app.api.v1.router import router as api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    root_path=f"/api/{settings.API_VERSION}",
    docs_url=settings.DOCS_URL_PATH,
    redoc_url=settings.REDOC_URL_PATH,
)

app.include_router(api_router)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
