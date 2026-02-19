from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.user import User
from app.schemas.user import UserCreate
from app.services.user import get_user_service

engine = create_async_engine(
    str(get_settings().SQLALCHEMY_DATABASE_URI), pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def initialize_database() -> None:
    settings = get_settings()
    service = get_user_service()
    async with AsyncSession(engine) as session:
        superuser = await service.get_by(session, User.email, settings.FIRST_SUPERUSER)
        if not superuser:
            user_in = UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                full_name="админ",
            )
            await service.create_superuser(session, user_in)

            logger.success("Initializing database. Created superuser successfully.")
        else:
            logger.success("Initializing database. Superuser already exists.")
