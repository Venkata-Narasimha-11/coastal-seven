"""Re-export Pydantic models and rebuild references for nested schemas."""

from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    Token,
    TokenPayload,
    UserRegister,
)
from app.schemas.common import HealthCheckResponse, MessageResponse, PaginatedResponse
from app.schemas.product import (
    ProductCreate,
    ProductDetailResponse,
    ProductResponse,
    ProductSummary,
    ProductUpdate,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserSummary,
    UserUpdate,
)

# Resolve circular references in nested schemas
UserDetailResponse.model_rebuild()
ProductDetailResponse.model_rebuild()

__all__ = [
    "HealthCheckResponse",
    "MessageResponse",
    "PaginatedResponse",
    "Token",
    "TokenPayload",
    "RefreshTokenRequest",
    "LoginRequest",
    "UserRegister",
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserSummary",
    "UserDetailResponse",
    "ProductCreate",
    "ProductUpdate",
    "ProductResponse",
    "ProductSummary",
    "ProductDetailResponse",
]
