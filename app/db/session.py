from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.models.base import Base

engine = create_async_engine(
    str(get_settings().SQLALCHEMY_DATABASE_URI), pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine, expire_on_commit=False, class_=AsyncSession
)


async def initialize_database() -> None:
    async with engine.begin() as async_conn:
        await async_conn.run_sync(Base.metadata.create_all)

        logger.success("Initializing database was successfull.")
