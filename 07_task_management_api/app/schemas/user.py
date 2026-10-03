"""User Pydantic schemas for request validation and serialization."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user properties shared across operations."""
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=100)
    role: UserRole = UserRole.DEVELOPER


class UserCreate(UserBase):
    """Payload for creating a new user (admin or self-service)."""
    password: str = Field(min_length=6, max_length=128)


class UserUpdate(BaseModel):
    """Payload for updating user profile or role."""
    full_name: Optional[str] = Field(default=None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(default=None, min_length=6, max_length=128)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserSummary(BaseModel):
    """Lightweight representation of a user for nested associations."""
    id: int
    username: str
    full_name: str
    role: UserRole

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Detailed user representation returned in API responses."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
