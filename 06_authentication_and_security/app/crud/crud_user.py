"""User CRUD Repository implementing database queries and password hashing via passlib."""

from typing import Optional, Union
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.auth import UserRegister
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User-specific repository with authentication, password hashing, and role support."""

    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[User]:
        """Fetch user by unique email."""
        statement = select(User).where(User.email == email.lower().strip())
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        """Fetch user by unique username."""
        statement = select(User).where(User.username == username.lower().strip())
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_by_email_or_username(
        self, session: AsyncSession, identifier: str
    ) -> Optional[User]:
        """Fetch user by either email or username."""
        cleaned = identifier.lower().strip()
        statement = select(User).where(
            or_(User.email == cleaned, User.username == cleaned)
        )
        result = await session.execute(statement)
        return result.scalars().first()

    async def get_with_products(self, session: AsyncSession, id: int) -> Optional[User]:
        """Fetch user with eager loaded owned products."""
        statement = select(User).options(selectinload(User.products)).where(User.id == id)
        result = await session.execute(statement)
        return result.scalars().first()

    async def create_with_hash(
        self, session: AsyncSession, obj_in: Union[UserCreate, UserRegister]
    ) -> User:
        """Create user with securely hashed password via passlib + bcrypt."""
        db_obj = User(
            username=obj_in.username.strip().lower(),
            email=obj_in.email.strip().lower(),
            hashed_password=get_password_hash(obj_in.password),
            full_name=obj_in.full_name,
            role=getattr(obj_in, "role", "user") or "user",
            is_active=getattr(obj_in, "is_active", True),
            is_superuser=getattr(obj_in, "is_superuser", False),
        )
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, session: AsyncSession, identifier: str, password: str
    ) -> Optional[User]:
        """Authenticate user against stored bcrypt hash using email or username."""
        user = await self.get_by_email_or_username(session, identifier)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update(
        self, session: AsyncSession, db_obj: User, obj_in: Union[UserUpdate, dict]
    ) -> User:
        """Update user, hashing password if updated."""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))

        return await super().update(session, db_obj, update_data)


crud_user = CRUDUser(User)
