import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from app.core.constants import Environment


class HealthResponse(BaseModel):
    status: str = Field(..., description="Статус состояния API", examples=["ok"])
    env: Environment = Field(
        ...,
        description="Среда окружения API",
        examples=[Environment.DEV, Environment.PROD, Environment.STAGE],
    )
    version: str = Field(..., description="Текущая версия API", examples=["1.0.0"])


class BaseDBModel(BaseModel):
    id: uuid.UUID = Field(..., description="ID пользователя")
    date_created: datetime = Field(..., description="Дата создания")
    date_updated: datetime = Field(..., description="Дата обновления")
