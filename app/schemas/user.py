from pydantic import BaseModel, EmailStr, Field, model_validator

from app.core.constants import UserRole


class UserBase(BaseModel):
    """
    Базовая схема пользователя
    """

    email: EmailStr = Field(
        ..., description="Email адрес пользователя", examples=["vinnipyx38@gmail.com"]
    )
    full_name: str | None = Field(
        None,
        description="Полное имя пользователя",
        min_length=2,
        max_length=255,
        examples=["Лёва"],
    )

    @model_validator(mode="before")
    def capitalize_full_name(cls, values):
        full_name = values.get("full_name")
        if full_name:
            values["full_name"] = full_name.strip().capitalize()
        return values


class UserCreate(UserBase):
    """
    Схема для создания нового пользователя
    """

    password: str = Field(min_length=8, max_length=72, examples=["myBestPassword"])


class UserUpdate(BaseModel):
    """
    Схема для обновления своего профиля
    """

    full_name: str | None = Field(
        None,
        description="Полное имя пользователя",
        min_length=2,
        max_length=255,
        examples=["Нелёва"],
    )

    @model_validator(mode="before")
    def capitalize_full_name(cls, values):
        full_name = values.get("full_name")
        if full_name:
            values["full_name"] = full_name.strip().capitalize()
        return values


class AdminUserUpdate(BaseModel):
    """
    Схема для обновления админом роли и статуса пользователя
    """

    role: UserRole | None = Field(
        None,
        description="Роль пользователя. Одна из двух 'admin' или 'user'",
        examples=["admin"],
    )
    is_active: bool | None = Field(
        None,
        description="Статус аккаунта пользователя. True - активен, False - отключен",
        examples=["True", "False"],
    )


class UserPublic(UserBase, AdminUserUpdate):
    """
    Публичная схема пользователя
    """

    role: UserRole | None = Field(
        None,
        description="Роль пользователя. Одна из двух 'admin' или 'user'",
        examples=["admin"],
    )
    is_active: bool | None = Field(
        None,
        description="Статус аккаунта пользователя. True - активен, False - отключен",
        examples=["True", "False"],
    )

    class Config:
        from_attributes = True
