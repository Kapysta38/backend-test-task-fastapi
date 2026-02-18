from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings
from app.core.config import Settings

router = APIRouter()


@router.get("/health-check")
async def health_check(
    settings: Settings = Depends(get_app_settings),
) -> dict[str, str]:
    return {
        "status": "ok",
        "env": settings.ENV,
        "version": settings.VERSION,
    }
