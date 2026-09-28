"""Pydantic V2 Schemas for Authentication and JWT Tokens."""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class Token(BaseModel):
    """JWT Bearer token response."""
    access_token: str = Field(..., description="Encoded JWT bearer token string")
    token_type: str = Field("bearer", description="Token authentication scheme")
    expires_in_minutes: int = Field(..., description="Validity lifetime in minutes")


class TokenPayload(BaseModel):
    """Decoded JWT payload data."""
    sub: Optional[str] = None
    exp: Optional[int] = None


class LoginRequest(BaseModel):
    """User credentials login request payload."""
    email: EmailStr = Field(..., description="Registered user email address")
    password: str = Field(..., min_length=1, description="Account password")
