from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.constants import UserRole
from app.core.exceptions import UserAlreadyExistsError
from app.core.security import hash_password, verify_password
from app.db.crud import CRUDFull
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class UserService(CRUDFull[User, UserCreate, UserUpdate]):
    async def authenticate(
        self, session: AsyncSession, email: EmailStr, password: str
    ) -> User | None:
        user = await self.get_by(session, self.model.email, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create(self, session: AsyncSession, obj_in: UserCreate) -> User:
        if await self.get_by(session, self.model.email, obj_in.email):
            raise UserAlreadyExistsError()
        obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hash_password(obj_in.password),
        )
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj

    async def create_superuser(self, session: AsyncSession, obj_in: UserCreate) -> User:
        if await self.get_by(session, User.email, obj_in.email):
            raise UserAlreadyExistsError()
        obj = self.model(
            email=obj_in.email,
            full_name=obj_in.full_name,
            hashed_password=hash_password(obj_in.password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


def get_user_service() -> UserService:
    return UserService(User)
