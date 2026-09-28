"""Export domain models for SQLAlchemy Base.metadata discovery."""

from app.models.product import Product
from app.models.user import User, UserRole

__all__ = ["Base", "User", "UserRole", "Product"]
