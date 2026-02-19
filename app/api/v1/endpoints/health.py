from fastapi import APIRouter, Depends

from app.api.deps import get_app_settings
from app.core.config import Settings
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health-check", response_model=HealthResponse)
async def health_check(
    settings: Settings = Depends(get_app_settings),
) -> HealthResponse:
    """
    Проверка работоспособности API.

    Возвращает текущий статус, версию и окружение сервиса API.
    """
    return HealthResponse(status="ok", env=settings.ENV, version=settings.VERSION)
