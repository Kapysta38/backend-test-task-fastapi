from typing import Literal

from pydantic import BaseModel, EmailStr, Field


class UserLogin(BaseModel):
    """
    Схема для авторизации пользователя по почте и паролю
    """

    email: EmailStr = Field(..., description="Email адрес пользователя")
    password: str = Field(
        ..., description="Пароль пользователя", min_length=8, max_length=72
    )


class Token(BaseModel):
    """
    Схема для access и refresh токенов
    """

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: Literal["bearer"] = Field("bearer", description="Схема авторизации")


class RefreshRequest(BaseModel):
    """
    Схема для обновления access токена
    """

    refresh_token: str = Field(..., description="JWT refresh token")
