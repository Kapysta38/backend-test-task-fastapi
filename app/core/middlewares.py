from collections.abc import Awaitable, Callable

from fastapi import Request, status
from starlette.responses import JSONResponse, Response

from app.core.config import get_settings
from app.core.redis import get_redis_client


async def rate_limit_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    redis = await get_redis_client()
    ip = request.client.host if request.client else "unknown"
    key = f"rate:{ip}"
    count = await redis.incr(key)
    if count == 1:
        await redis.expire(key, 60)

    if count > get_settings().MAX_REQUESTS_PER_MINUTE:
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": "Too many requests"},
        )

    return await call_next(request)
