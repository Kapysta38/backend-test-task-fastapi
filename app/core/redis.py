from redis import asyncio as aioredis

from app.core.config import get_settings

settings = get_settings()

redis = aioredis.from_url(
    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0",
    encoding="utf-8",
    decode_responses=True,
)
