from typing import TypeVar

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select

T = TypeVar("T")


async def generate_unique_slug(
    session: AsyncSession,
    model: type[T],
    value: str,
    slug_field_name: str = "slug",
) -> str:
    """
    Генерирует уникальный slug для любой модели
    При конфликте добавляет суффикс -1, -2 и т.д.
    """
    base_slug = slug = slugify(value)
    counter = 1

    while True:
        stmt: Select[tuple[T]] = select(model).where(
            getattr(model, slug_field_name) == slug
        )
        existing = await session.scalar(stmt)
        if not existing:
            break
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
