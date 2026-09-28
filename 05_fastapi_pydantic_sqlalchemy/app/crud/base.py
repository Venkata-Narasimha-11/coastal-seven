"""Generic CRUD base class implementing modern SQLAlchemy 2.0 async operations."""

from typing import Any, Dict, Generic, List, Optional, Tuple, Type, TypeVar, Union
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Base

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD repository with async SQLAlchemy 2.0 select, insert, update, and delete."""

    def __init__(self, model: Type[ModelType]) -> None:
        """CRUD object with default methods to Create, Read, Update, Delete (CRUD)."""
        self.model = model

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        statement = select(self.model).where(self.model.id == id)
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> Tuple[List[ModelType], int]:
        """Fetch multiple records with pagination and total count."""
        count_stmt = select(func.count()).select_from(self.model)
        total = await session.scalar(count_stmt) or 0

        stmt = select(self.model).offset(skip).limit(limit).order_by(self.model.id.asc())
        result = await session.execute(stmt)
        items = list(result.scalars().all())
        return items, total

    async def create(
        self, session: AsyncSession, obj_in: Union[CreateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        """Insert and persist a new record."""
        if isinstance(obj_in, dict):
            obj_data = obj_in
        else:
            obj_data = obj_in.model_dump()

        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]],
    ) -> ModelType:
        """Update an existing record with partial or full dictionary/schema data."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def remove(self, session: AsyncSession, id: int) -> Optional[ModelType]:
        """Delete a record by primary key."""
        obj = await self.get(session, id)
        if obj:
            await session.delete(obj)
            await session.flush()
        return obj

    async def count(self, session: AsyncSession) -> int:
        """Return total row count."""
        statement = select(func.count()).select_from(self.model)
        total = await session.scalar(statement)
        return total or 0
