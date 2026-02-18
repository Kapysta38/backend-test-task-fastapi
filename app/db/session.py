from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings

engine = create_async_engine(
    str(get_settings().SQLALCHEMY_DATABASE_URI), pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def initialize_database() -> None:
    async with engine.begin() as _:
        logger.success("Initializing database was successfull.")
