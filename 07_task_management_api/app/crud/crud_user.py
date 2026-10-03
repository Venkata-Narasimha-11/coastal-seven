"""CRUD repository for User entities and authentication queries."""

from typing import Any, Dict, Optional, Union
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """User repository with authentication logic."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Fetch user by case-insensitive email address."""
        result = await db.execute(select(User).where(User.email == email.lower().strip()))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Fetch user by case-insensitive username."""
        result = await db.execute(select(User).where(User.username == username.strip()))
        return result.scalars().first()

    async def get_by_username_or_email(self, db: AsyncSession, identifier: str) -> Optional[User]:
        """Fetch user by either username or email address."""
        clean_id = identifier.strip()
        result = await db.execute(
            select(User).where(
                or_(
                    User.username == clean_id,
                    User.email == clean_id.lower(),
                )
            )
        )
        return result.scalars().first()

    async def authenticate(
        self,
        db: AsyncSession,
        username_or_email: str,
        password: str,
    ) -> Optional[User]:
        """Authenticate user by credentials and password verification."""
        user = await self.get_by_username_or_email(db, username_or_email)
        if not user or not user.is_active:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create(self, db: AsyncSession, obj_in: Union[UserCreate, Dict[str, Any]]) -> User:
        """Create a new user with securely hashed password."""
        if isinstance(obj_in, dict):
            create_data = obj_in.copy()
        else:
            create_data = obj_in.model_dump()

        password = create_data.pop("password")
        create_data["hashed_password"] = get_password_hash(password)
        create_data["email"] = create_data["email"].lower().strip()
        create_data["username"] = create_data["username"].strip()

        db_user = User(**create_data)
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    async def update(
        self,
        db: AsyncSession,
        db_obj: User,
        obj_in: Union[UserUpdate, Dict[str, Any]],
    ) -> User:
        """Update user record, hashing password if provided."""
        if isinstance(obj_in, dict):
            update_data = obj_in.copy()
        else:
            update_data = obj_in.model_dump(exclude_unset=True)

        if "password" in update_data and update_data["password"]:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        elif "password" in update_data:
            update_data.pop("password")

        if "email" in update_data and update_data["email"]:
            update_data["email"] = update_data["email"].lower().strip()

        return await super().update(db, db_obj, update_data)


user_crud = CRUDUser()
