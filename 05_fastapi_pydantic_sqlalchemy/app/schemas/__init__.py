"""Schemas package exposing Pydantic V2 request and response contracts."""

from app.schemas.common import (
    HealthCheckResponse,
    MessageResponse,
    PaginatedResponse,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserSummary,
    UserUpdate,
)
from app.schemas.product import (
    ProductBase,
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    ProductSummary,
    ProductUpdate,
)

from app.schemas.auth import (
    LoginRequest,
    Token,
    TokenPayload,
)

__all__ = [
    "HealthCheckResponse",
    "MessageResponse",
    "PaginatedResponse",
    "UserBase",
    "UserCreate",
    "UserDetailResponse",
    "UserResponse",
    "UserSummary",
    "UserUpdate",
    "ProductBase",
    "ProductCreate",
    "ProductDetailResponse",
    "ProductResponse",
    "ProductSummary",
    "ProductUpdate",
    "LoginRequest",
    "Token",
    "TokenPayload",
]
