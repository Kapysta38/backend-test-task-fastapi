import uuid
from collections.abc import AsyncGenerator, Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.constants import UserRole
from app.db.session import AsyncSessionLocal
from app.models.user import User
from app.services.category import CategoryService, get_category_service
from app.services.post import PostService, get_post_service
from app.services.user import UserService, get_user_service

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"/api/{get_settings().API_VERSION}/auth/login"
)
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_app_settings() -> Settings:
    return get_settings()


SettingsDep = Annotated[Settings, Depends(get_app_settings)]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError as e:
        logger.error("Unable to yield session in database dependency")
        logger.error(e)
        raise e


SessionDep = Annotated[AsyncSession, Depends(get_db)]

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

PostServiceDep = Annotated[PostService, Depends(get_post_service)]
CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]


async def get_current_user(
    session: SessionDep,
    user_service: UserServiceDep,
    token: TokenDep,
    settings: SettingsDep,
) -> User:
    unauthorized_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    forbidden_exc = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="User is not active or no permission",
    )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id: uuid.UUID | None = payload.get("sub")

        if user_id is None:
            raise unauthorized_exc

    except JWTError:
        raise unauthorized_exc

    user = await user_service.get(session, user_id)
    if not user:
        raise unauthorized_exc
    if not user.is_active:
        raise forbidden_exc

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: UserRole) -> Callable[..., User]:
    def checker(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Denied permissions"
            )

        return user

    return checker


AdminUser = Annotated[User, Depends(require_role(UserRole.ADMIN))]
