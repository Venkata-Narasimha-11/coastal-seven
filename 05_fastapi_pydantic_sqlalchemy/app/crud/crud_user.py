"""User CRUD Repository implementing SQLAlchemy 2.0 async queries."""

from typing import List, Optional, Tuple, Union
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import hash_password, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """Specialized CRUD operations for User entities."""

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Lookup a user by unique email address."""
        stmt = select(User).where(User.email == email.strip().lower())
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        """Lookup a user by unique username."""
        stmt = select(User).where(User.username == username.strip().lower())
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_with_products(self, session: AsyncSession, user_id: int) -> Optional[User]:
        """Fetch user with eager loaded products relationship."""
        stmt = (
            select(User)
            .options(selectinload(User.products))
            .where(User.id == user_id)
        )
        result = await session.execute(stmt)
        return result.scalars().first()

    async def get_multi_filtered(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        is_active: Optional[bool] = None,
    ) -> Tuple[List[User], int]:
        """Fetch paginated users with optional active status filter."""
        query = select(User)
        count_query = select(func.count()).select_from(User)

        if is_active is not None:
            query = query.where(User.is_active == is_active)
            count_query = count_query.where(User.is_active == is_active)

        total = await session.scalar(count_query) or 0
        paginated_query = query.offset(skip).limit(limit).order_by(User.id.asc())
        result = await session.execute(paginated_query)
        users = list(result.scalars().all())
        return users, total

    async def create_user(self, session: AsyncSession, obj_in: UserCreate) -> User:
        """Create a user with a securely hashed password."""
        hashed_pw = hash_password(obj_in.password)
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            hashed_password=hashed_pw,
            full_name=obj_in.full_name,
            is_active=obj_in.is_active,
            is_superuser=obj_in.is_superuser,
        )
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def update_user(
        self,
        session: AsyncSession,
        db_obj: User,
        obj_in: Union[UserUpdate, dict],
    ) -> User:
        """Update user record, re-hashing password if one is supplied."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            hashed_pw = hash_password(update_data["password"])
            db_obj.hashed_password = hashed_pw
            del update_data["password"]

        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, session: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        """Authenticate user by email and plain password."""
        user = await self.get_by_email(session, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user


crud_user = CRUDUser(User)
