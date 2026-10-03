"""Authentication schemas for login, registration, and JWT token management."""

from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from app.models.user import UserRole


class Token(BaseModel):
    """JWT Token response returned upon successful authentication."""
    access_token: str = Field(description="Signed JWT access token")
    refresh_token: str = Field(description="Signed JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(description="Access token expiration in seconds")


class TokenPayload(BaseModel):
    """Decoded JWT payload structure."""
    sub: Optional[str] = None
    role: Optional[str] = None
    exp: Optional[int] = None
    type: Optional[str] = None


class LoginRequest(BaseModel):
    """JSON credentials payload for login."""
    username: str = Field(min_length=3, max_length=50, description="Username or email")
    password: str = Field(min_length=6, description="Plain text password")


class RegisterRequest(BaseModel):
    """Payload for registering a new user."""
    username: str = Field(min_length=3, max_length=50, pattern=r"^[a-zA-Z0-9_-]+$")
    email: EmailStr
    password: str = Field(min_length=6, max_length=128, description="Minimum 6 characters")
    full_name: str = Field(min_length=2, max_length=100)
    role: Optional[UserRole] = Field(default=UserRole.DEVELOPER, description="Requested role")

    model_config = ConfigDict(from_attributes=True)


class RefreshTokenRequest(BaseModel):
    """Payload containing refresh token to exchange for new access token."""
    refresh_token: str = Field(description="Valid JWT refresh token")
