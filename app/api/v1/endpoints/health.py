from fastapi import APIRouter

from app.api.deps import SettingsDep
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/health-check", response_model=HealthResponse)
async def health_check(
    settings: SettingsDep,
) -> HealthResponse:
    """
    Проверка работоспособности API.

    Возвращает текущий статус, версию и окружение сервиса API.
    """
    return HealthResponse(status="ok", env=settings.ENV, version=settings.VERSION)
