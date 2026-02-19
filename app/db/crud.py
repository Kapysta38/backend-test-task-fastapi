from collections.abc import Sequence
from typing import Any, Generic, TypeVar

from pydantic import BaseModel
from sqlalchemy import ColumnElement, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import InstrumentedAttribute

from app.core.constants import OrderDirection
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)

Filter = ColumnElement[bool]
ColumnType = ColumnElement[Any] | InstrumentedAttribute[Any]


class CRUDRead(Generic[ModelType]):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> ModelType | None:
        return await session.get(self.model, id)

    async def get_by(
        self,
        session: AsyncSession,
        column: ColumnType,
        value: Any,
    ) -> ModelType | None:
        stmt = select(self.model).where(column == value)

        result = await session.scalars(stmt)

        return result.first()

    async def paginate(
        self,
        session: AsyncSession,
        *filters: Filter,
        page: int = 1,
        size: int = 100,
        order_by: ColumnType | None = None,
        order_dir: OrderDirection = OrderDirection.ASC,
    ) -> tuple[Sequence[ModelType], int]:
        offset = (page - 1) * size

        if order_by is None:
            order_by = self.model.id

        if order_dir is OrderDirection.DESC:
            column = order_by.desc()
        else:
            column = order_by.asc()

        stmt = select(self.model).order_by(column).offset(offset).limit(size)

        if filters:
            stmt = stmt.where(*filters)

        items = (await session.scalars(stmt)).all()

        total = await session.scalar(select(func.count()).select_from(self.model)) or 0

        return items, total


class CRUDRemove(CRUDRead[ModelType]):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def remove(self, session: AsyncSession, id: Any) -> ModelType | None:
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.commit()
        return obj


class CRUDCreate(CRUDRead[ModelType], Generic[ModelType, CreateSchemaType]):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        obj: ModelType = self.model(**obj_in.model_dump())
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        return obj


class CRUDUpdate(CRUDRead[ModelType], Generic[ModelType, UpdateSchemaType]):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)

    async def update(
        self, session: AsyncSession, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj


class CRUDFull(
    CRUDRemove[ModelType],
    CRUDCreate[ModelType, CreateSchemaType],
    CRUDUpdate[ModelType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    def __init__(self, model: type[ModelType]):
        super().__init__(model)
