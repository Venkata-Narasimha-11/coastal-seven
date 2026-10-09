"""Pydantic V2 schemas for user management and authentication."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from app.models.user import UserRole


class Token(BaseModel):
    """Access and refresh token response."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Payload decoded from JWT token."""
    sub: str
    role: str
    exp: int


class UserBase(BaseModel):
    """Shared user properties."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=255)


class UserCreate(UserBase):
    """Schema for registering a new user."""
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    role: Optional[UserRole] = UserRole.CUSTOMER


class UserLogin(BaseModel):
    """Schema for user login credentials."""
    username: str = Field(..., description="Username or Email", json_schema_extra={"example": "admin"})
    password: str = Field(..., description="Account password", json_schema_extra={"example": "AdminPassword123!"})


class UserUpdate(BaseModel):
    """Schema for updating user profile."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)


class UserResponse(UserBase):
    """Public user response schema."""
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
