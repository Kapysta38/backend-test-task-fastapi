from pydantic import BaseModel, Field

from app.schemas.common import BaseDBModel


class CategoryCreate(BaseModel):
    """
    Схема для создания категории
    """

    name: str = Field(
        ...,
        description="Уникальное название категории",
        max_length=100,
        examples=["Моя будущая работа"],
    )


class CategoryUpdate(BaseModel):
    """
    Схема для обновления названия категории
    """

    name: str | None = Field(
        None,
        description="Уникальное название категории",
        max_length=100,
        examples=["Моя будущая работа"],
    )


class CategoryPublic(CategoryCreate, BaseDBModel):
    """
    Публичная схема категории

    Содержит метаданные: ID, дату создания, дату обновления
    """

    slug: str = Field(
        ...,
        description="Slug значение",
        max_length=255,
        examples=["moia-budushuia-rabota"],
    )

    class Config:
        from_attributes = True
