"""Export router endpoints."""

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.products import router as products_router
from app.api.v1.endpoints.users import router as users_router

__all__ = ["auth_router", "users_router", "products_router"]
