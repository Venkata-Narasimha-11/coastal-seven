"""Pydantic V2 Schemas for User entity."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

if TYPE_CHECKING:
    from app.schemas.product import ProductSummary


class UserBase(BaseModel):
    """Base user schema containing shared attributes."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Alphanumeric username with optional underscores (3-50 chars)",
        examples=["john_doe"],
    )
    email: EmailStr = Field(
        ...,
        description="Valid, unique email address",
        examples=["john.doe@example.com"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's full legal or display name",
        examples=["John Doe"],
    )
    is_active: bool = Field(
        True,
        description="Whether the user account is active",
    )

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        """Field validator: normalize username to lowercase and strip whitespace."""
        if isinstance(v, str):
            cleaned = v.strip().lower()
            if len(cleaned) < 3:
                raise ValueError("Username must be at least 3 characters after trimming")
            return cleaned
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        """Field validator: ensure email is normalized to lowercase and trimmed."""
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserCreate(UserBase):
    """Schema for registering a new user, requiring password confirmation."""
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain text password with minimum 8 characters",
        examples=["StrongP@ssw0rd!"],
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password confirmation, must match password exactly",
        examples=["StrongP@ssw0rd!"],
    )
    is_superuser: bool = Field(
        False,
        description="Designates whether the user has administrator privileges",
    )

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Field validator: check password complexity requirements."""
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in v):
            raise ValueError("Password must contain at least one letter")
        return v

    @model_validator(mode="after")
    def verify_password_match(self) -> "UserCreate":
        """Model validator: cross-validate password and confirm_password match."""
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation password do not match")
        return self


class UserUpdate(BaseModel):
    """Schema for updating an existing user (all fields optional for PATCH)."""
    username: Optional[str] = Field(
        None,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
    )
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=8, max_length=128)
    is_active: Optional[bool] = None

    @field_validator("username", mode="before")
    @classmethod
    def normalize_update_username(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_update_email(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class UserSummary(BaseModel):
    """Lightweight summary schema for embedding inside Product responses."""
    id: int = Field(..., description="Unique user ID")
    username: str = Field(..., description="Username")
    email: EmailStr = Field(..., description="Email address")
    full_name: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    """Response schema returned to clients when querying users."""
    id: int = Field(..., description="Unique user identifier")
    is_superuser: bool = Field(..., description="Admin privileges flag")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    # Pydantic V2 replacement for orm_mode = True
    model_config = ConfigDict(from_attributes=True)


class UserDetailResponse(UserResponse):
    """Detailed response schema including nested products owned by the user."""
    products: List["ProductSummary"] = Field(
        default_factory=list,
        description="List of catalog products owned by this user",
    )

    model_config = ConfigDict(from_attributes=True)
