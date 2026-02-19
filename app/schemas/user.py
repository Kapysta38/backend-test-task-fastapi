from pydantic import BaseModel, EmailStr, Field

from app.core.constants import UserRole


class UserBase(BaseModel):
    email: EmailStr = Field(..., description="Email адрес пользователя")
    full_name: str | None = Field(
        None, description="Полное имя пользователя", min_length=2, max_length=255
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=72)


class UserUpdate(BaseModel):
    full_name: str | None = Field(
        None, description="Полное имя пользователя", min_length=2, max_length=255
    )


class AdminUserUpdate(BaseModel):
    role: UserRole | None = Field(None, description="Роль пользователя")
    is_active: bool | None = Field(None, description="Статус аккаунта пользователя")


class UserPublic(UserBase):
    is_active: bool = Field(..., description="Статус аккаунта пользователя")
    role: UserRole = Field(UserRole.USER, description="Роль пользователя")

    class Config:
        from_attributes = True
