"""FastAPI dependencies for request handling, database sessions, and query params."""

from typing import Annotated, Optional
from fastapi import Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_db

# Database session dependency
SessionDep = Annotated[AsyncSession, Depends(get_async_db)]


class PaginationParams:
    """Dependency for collection pagination parameters."""

    def __init__(
        self,
        skip: int = Query(0, ge=0, description="Number of records to skip (offset)"),
        limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return (page size)"),
    ) -> None:
        self.skip = skip
        self.limit = limit
        self.page = (skip // limit) + 1


class ProductFilterParams:
    """Dependency for product catalog query parameter filtering."""

    def __init__(
        self,
        search: Optional[str] = Query(None, min_length=1, max_length=100, description="Full-text search in title, description, or SKU"),
        category: Optional[str] = Query(None, min_length=2, max_length=50, description="Filter by exact category name"),
        min_price: Optional[float] = Query(None, ge=0, description="Minimum price boundary"),
        max_price: Optional[float] = Query(None, ge=0, description="Maximum price boundary"),
        is_available: Optional[bool] = Query(None, description="Filter by availability status"),
        owner_id: Optional[int] = Query(None, ge=1, description="Filter products by owner user ID"),
    ) -> None:
        self.search = search
        self.category = category
        self.min_price = min_price
        self.max_price = max_price
        self.is_available = is_available
        self.owner_id = owner_id
