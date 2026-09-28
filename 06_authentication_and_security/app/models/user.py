"""SQLAlchemy 2.0 User Domain Model with RBAC Role Support."""

from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.product import Product


class UserRole(str, Enum):
    """User authorization roles."""
    ADMIN = "admin"
    USER = "user"


class User(Base, TimestampMixin):
    """User entity representing registered users, admins, and catalog managers."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default=UserRole.USER.value, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # 1-to-many relationship: One user can own multiple products
    products: Mapped[List["Product"]] = relationship(
        "Product",
        back_populates="owner",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    @property
    def is_admin(self) -> bool:
        """Helper to determine administrative privileges."""
        return self.role == UserRole.ADMIN.value or self.is_superuser

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role}'>"
