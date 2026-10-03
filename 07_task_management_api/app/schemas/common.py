"""Common generic Pydantic schemas including pagination and responses."""

from datetime import datetime, timezone
import math
from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Standard pagination query parameters."""
    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    limit: int = Field(default=10, ge=1, le=100, description="Items per page")

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized envelope for paginated collections."""
    items: List[T]
    total: int = Field(description="Total count matching filter criteria")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    total_pages: int = Field(description="Calculated total pages available")
    has_next: bool = Field(description="Indicates whether next page exists")
    has_prev: bool = Field(description="Indicates whether previous page exists")

    model_config = ConfigDict(from_attributes=True)

    @classmethod
    def create(cls, items: List[T], total: int, page: int, limit: int) -> "PaginatedResponse[T]":
        total_pages = math.ceil(total / limit) if limit > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            limit=limit,
            total_pages=total_pages,
            has_next=page < total_pages,
            has_prev=page > 1,
        )


class ApiResponse(BaseModel, Generic[T]):
    """Uniform API wrapper for responses."""
    success: bool = True
    message: Optional[str] = None
    data: Optional[T] = None


class HealthCheckResponse(BaseModel):
    """System health check model."""
    status: str = "ok"
    database: bool
    version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
