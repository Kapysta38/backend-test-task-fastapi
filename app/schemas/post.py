import uuid

from pydantic import BaseModel, Field

from app.schemas.common import BaseDBModel


class PostBase(BaseModel):
    """
    Базовая схема для постов
    """

    title: str = Field(
        ...,
        description="Заголовок поста",
        max_length=255,
        examples=["Мой первый пост!"],
    )


class PostCreate(PostBase):
    """
    Схема для создания поста
    """

    category_id: uuid.UUID = Field(..., description="ID категории")
    content_html: str = Field(
        ..., description="HTML контент поста", examples=["<div>Hello work!</div>"]
    )


class PostUpdate(BaseModel):
    """
    Схема для обновления заголовка и текста поста
    """

    title: str | None = Field(
        None,
        description="Заголовок поста",
        max_length=255,
        examples=["Мой первый пост!"],
    )
    content_html: str | None = Field(
        None, description="HTML контент поста", examples=["<div>Hello work!</div>"]
    )


class PostPublic(PostBase, BaseDBModel):
    """
    Публичная схема для отображения постов в общем списке

    Содержит метаданные: ID, дату создания, дату обновления
    """

    slug: str = Field(
        ..., description="Slug значение", max_length=255, examples=["moi-pervyi-post"]
    )
    category_id: uuid.UUID = Field(..., description="ID категории")

    class Config:
        from_attributes = True


class PostContent(PostBase, BaseDBModel):
    """
    Публичная схема для отображения поста детально

    Содержит метаданные: ID, дату создания, дату обновления
    """

    slug: str = Field(
        ..., description="Slug значение", max_length=255, examples=["moi-pervyi-post"]
    )
    category_id: uuid.UUID = Field(..., description="ID категории")
    content_html: str = Field(
        ..., description="HTML контент поста", examples=["<div>Hello work!</div>"]
    )

    class Config:
        from_attributes = True
