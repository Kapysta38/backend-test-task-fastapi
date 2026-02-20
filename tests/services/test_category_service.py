import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from app.services.category import CategoryService


@pytest.mark.asyncio
class TestCategoryService:
    @pytest.mark.asyncio
    async def test_create_category(self, test_db: AsyncSession):
        service = CategoryService(Category)
        category_in = CategoryCreate(name="Технолоджия!")

        category = await service.create(test_db, category_in)

        assert category.name == "Технолоджия!"
        assert category.slug == "tekhnolodzhiia"
        assert category.id is not None

    @pytest.mark.asyncio
    async def test_update_category(self, test_db: AsyncSession, test_category):
        service = CategoryService(Category)
        update_data = CategoryUpdate(name="Обновления")

        updated = await service.update(test_db, test_category, update_data)

        assert updated.name == "Обновления"

    @pytest.mark.asyncio
    async def test_get_category(self, test_db: AsyncSession, test_category):
        service = CategoryService(Category)

        category = await service.get(test_db, test_category.id)

        assert category is not None
        assert category.id == test_category.id

    @pytest.mark.asyncio
    async def test_delete_category(self, test_db: AsyncSession, test_category):
        service = CategoryService(Category)

        deleted = await service.remove(test_db, test_category.id)
        category_after = await service.get(test_db, test_category.id)

        assert deleted.id == test_category.id
        assert category_after is None
