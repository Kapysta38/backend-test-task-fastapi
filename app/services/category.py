from sqlalchemy.ext.asyncio import AsyncSession

from app.core.utils import generate_unique_slug
from app.db.crud import CRUDFull
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


class CategoryService(CRUDFull[Category, CategoryCreate, CategoryUpdate]):
    CATEGORY_ORDER_FIELDS = {
        "name": Category.name,
        "date_created": Category.date_created,
    }

    async def create(self, session: AsyncSession, obj_in: CategoryCreate) -> Category:
        slug = await generate_unique_slug(session, self.model, obj_in.name)
        obj_data = obj_in.model_dump()
        obj_data["slug"] = slug
        obj = self.model(**obj_data)
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


def get_category_service() -> CategoryService:
    return CategoryService(Category)
