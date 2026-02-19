from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep, SettingsDep, UserServiceDep
from app.core.exceptions import UserAlreadyExistsError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    verify_refresh_token,
)
from app.models.user import User
from app.schemas.auth import RefreshRequest, Token
from app.schemas.user import UserCreate, UserPublic

router = APIRouter()


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
async def register(
    session: SessionDep, service: UserServiceDep, user_in: UserCreate
) -> User:
    """
    Регистрация нового пользователя.
    """
    try:
        return await service.create(session, user_in)
    except UserAlreadyExistsError:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    service: UserServiceDep,
    settings: SettingsDep,
    form: OAuth2PasswordRequestForm = Depends(),
) -> Token:
    """
    Авторизация пользователя

    Возвращает access и refresh токен
    """
    user = await service.authenticate(
        session,
        form.username,
        form.password,
    )
    if not user:
        raise HTTPException(
            401,
            "Invalid email or password",
        )
    data = {"sub": str(user.id)}
    access_token = create_access_token(
        data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    refresh_token = create_refresh_token(
        data, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/refresh")
async def refresh(
    session: SessionDep,
    service: UserServiceDep,
    settings: SettingsDep,
    request: RefreshRequest,
) -> Token:
    """
    Обновление access и refresh токена по refresh-токену.

    Возвращает новые access и refresh токен
    """
    payload = verify_refresh_token(request.refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    user = await service.get(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User inactive or not found",
        )

    data = {"sub": str(user.id)}
    new_access_token = create_access_token(
        data, expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    new_refresh_token = create_refresh_token(
        data, expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


# TODO: Для большей безопасности лучше хранить рефреш токен в куках и добавить запрос на его удаление
# Но по заданию этого не было указано. поэтому просто решил оставить коммент :)
# @router.post("/logout")
# async def logout(response: Response):
#     """
#     Удаление refresh-токена из кук.
#     """
#     response.delete_cookie(
#         key="refresh_token",
#         httponly=True,
#         samesite="lax",
#         secure=True,
#     )
#     return {"detail": "Successfully logged out"}
