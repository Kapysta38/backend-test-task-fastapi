import asyncio
import uuid
from collections.abc import AsyncGenerator
from unittest.mock import AsyncMock, patch

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import get_settings
from app.core.constants import UserRole
from app.core.security import hash_password
from app.models.base import Base
from app.models.category import Category
from app.models.post import Post
from app.models.user import User

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
def settings():
    return get_settings()


@pytest_asyncio.fixture(scope="session")
async def test_db_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def test_db(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(bind=test_db_engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def mock_redis():
    redis_mock = AsyncMock()
    redis_mock.incr = AsyncMock(return_value=1)
    redis_mock.expire = AsyncMock(return_value=True)
    return redis_mock


@pytest_asyncio.fixture
async def test_client(test_db: AsyncSession, mock_redis):
    with patch("app.core.redis.get_redis_client", return_value=mock_redis):
        from app.api.deps import get_db
        from app.main import app

        async def override_get_db():
            yield test_db

        app.dependency_overrides[get_db] = override_get_db

        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            yield client

        app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(test_db: AsyncSession) -> User:
    user = User(
        id=uuid.uuid4(),
        email=f"test-{uuid.uuid4().hex}@example.com",
        full_name="Нелёва",
        hashed_password=hash_password("ЯНастоящийЛёва"),
        role=UserRole.USER,
        is_active=True,
    )
    test_db.add(user)
    await test_db.flush()
    return user


@pytest_asyncio.fixture
async def admin_user(test_db: AsyncSession) -> User:
    admin = User(
        id=uuid.uuid4(),
        email=f"admin-{uuid.uuid4().hex}@example.com",
        full_name="Лёва",
        hashed_password=hash_password("топсикретпассворд"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    test_db.add(admin)
    await test_db.flush()
    return admin


@pytest_asyncio.fixture
async def test_category(test_db: AsyncSession) -> Category:
    category = Category(
        id=uuid.uuid4(),
        name=f"Эх, вот бы устроится в ITWorld!{uuid.uuid4().hex}",
        slug=f"test-category-slug-{uuid.uuid4().hex}",
    )
    test_db.add(category)
    await test_db.flush()
    return category


@pytest_asyncio.fixture
async def test_post(test_db: AsyncSession, test_category: Category) -> Post:
    post = Post(
        id=uuid.uuid4(),
        title="Мое тестовое задание",
        content_html="<p>Постарался на славу, даже xss атаки защищаю</p>",
        slug=f"test-post-slug-{uuid.uuid4().hex}",
        category_id=test_category.id,
    )
    test_db.add(post)
    await test_db.flush()
    return post
