import uuid
from typing import TYPE_CHECKING

import bleach
from sqlalchemy import UUID, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.config import get_settings
from app.models.base import Base

if TYPE_CHECKING:
    from app.models.category import Category


class Post(Base):
    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content_html: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )

    category_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("categories.id"))
    category: Mapped["Category"] = relationship("Category", back_populates="posts")

    def set_content_html(self, html_content: str) -> None:
        """
        Санитизация HTML входных данных.
        """
        settings = get_settings()
        self.content_html = bleach.clean(
            html_content,
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            strip=True,
        )
