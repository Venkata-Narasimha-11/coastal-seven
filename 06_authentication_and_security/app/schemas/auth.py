"""Pydantic V2 Schemas for Authentication, Tokens, and Registration."""

from typing import List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator


class Token(BaseModel):
    """JWT Bearer token response returning access and refresh tokens."""
    access_token: str = Field(..., description="Signed JWT access token string")
    refresh_token: str = Field(..., description="Signed JWT refresh token string")
    token_type: str = Field("bearer", description="Token scheme designation")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Payload to request access token renewal using a valid refresh token."""
    refresh_token: str = Field(..., min_length=10, description="Valid JWT refresh token")


class LoginRequest(BaseModel):
    """JSON credentials payload for user login."""
    email: EmailStr = Field(..., description="Registered user email address")
    password: str = Field(..., min_length=1, description="Account password")


class TokenPayload(BaseModel):
    """Decoded JWT claims representation."""
    sub: Optional[str] = None
    type: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None
    roles: Optional[List[str]] = None


class UserRegister(BaseModel):
    """Schema for registering a new user account with role selection."""
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_]+$",
        description="Alphanumeric username with optional underscores (3-50 chars)",
        examples=["alice_admin"],
    )
    email: EmailStr = Field(
        ...,
        description="Unique contact and login email address",
        examples=["alice@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password with at least 8 characters, letters, and numbers",
        examples=["SecretPass123!"],
    )
    confirm_password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password confirmation, must match password exactly",
        examples=["SecretPass123!"],
    )
    full_name: Optional[str] = Field(
        None,
        max_length=100,
        description="User's full display name",
        examples=["Alice Wonderland"],
    )
    role: str = Field(
        "user",
        description="Assigned role: 'user' or 'admin'",
        examples=["user"],
    )

    @field_validator("username", mode="before")
    @classmethod
    def normalize_username(cls, v: str) -> str:
        if isinstance(v, str):
            cleaned = v.strip().lower()
            if len(cleaned) < 3:
                raise ValueError("Username must have at least 3 characters after trimming")
            return cleaned
        return v

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        cleaned = v.strip().lower()
        if cleaned not in ("user", "admin"):
            raise ValueError("Role must be either 'user' or 'admin'")
        return cleaned

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        if not any(c.isdigit() for c in v):
            raise ValueError("Password must contain at least one digit")
        if not any(c.isalpha() for c in v):
            raise ValueError("Password must contain at least one letter")
        return v

    @model_validator(mode="after")
    def verify_password_match(self) -> "UserRegister":
        if self.password != self.confirm_password:
            raise ValueError("Password and confirmation password do not match")
        return self
