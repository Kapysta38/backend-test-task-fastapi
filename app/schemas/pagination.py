from typing import Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: list[T] = Field(..., description="Список элементов на текущей странице")

    total: int = Field(
        ..., ge=0, description="Общее количество элементов с учётом фильтров"
    )

    page: int = Field(1, ge=1, description="Номер текущей страницы (начиная с 1)")

    size: int = Field(
        20, ge=1, le=100, description="Количество элементов на странице (от 1 до 100)"
    )

    pages: int = Field(..., ge=1, description="Общее количество страниц")
