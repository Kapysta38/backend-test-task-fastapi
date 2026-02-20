import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UserAlreadyExistsError
from app.core.security import verify_password
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.mark.asyncio
class TestUserService:
    @pytest.mark.asyncio
    async def test_create_user(self, test_db: AsyncSession):
        service = UserService(User)
        user_in = UserCreate(
            email="noncreateduser@example.com",
            full_name="name",
            password="securepass123",
        )

        user = await service.create(test_db, user_in)

        assert user.email == "noncreateduser@example.com"
        assert user.full_name == "Name"
        assert verify_password("securepass123", user.hashed_password)

    @pytest.mark.asyncio
    async def test_create_duplicate_user(self, test_db: AsyncSession, test_user):
        service = UserService(User)
        user_in = UserCreate(
            email=test_user.email,
            full_name="Duplicate",
            password="12345678",
        )
        with pytest.raises(UserAlreadyExistsError):
            await service.create(test_db, user_in)

    @pytest.mark.asyncio
    async def test_authenticate_user(self, test_db: AsyncSession, test_user):
        service = UserService(User)
        user = await service.authenticate(test_db, test_user.email, "ЯНастоящийЛёва")
        assert user is not None
        assert user.email == test_user.email

    @pytest.mark.asyncio
    async def test_authenticate_invalid_password(
        self, test_db: AsyncSession, test_user
    ):
        service = UserService(User)
        user = await service.authenticate(test_db, test_user.email, "wrongpassword")
        assert user is None

    @pytest.mark.asyncio
    async def test_authenticate_nonexistent_user(self, test_db: AsyncSession):
        service = UserService(User)
        user = await service.authenticate(
            test_db, "nonexistent@example.com", "password"
        )
        assert user is None
