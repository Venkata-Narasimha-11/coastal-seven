"""Common reusable Pydantic V2 schemas."""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Standard message response structure."""
    message: str = Field(..., description="Human-readable response message")
    detail: Optional[str] = Field(None, description="Optional additional detail")


class HealthCheckResponse(BaseModel):
    """System health check response."""
    status: str = Field(..., description="Application operational status")
    database: str = Field(..., description="PostgreSQL connectivity status")
    version: str = Field(..., description="API semantic version")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic pagination wrapper for collection endpoints."""
    total: int = Field(..., ge=0, description="Total count of matching records")
    page: int = Field(..., ge=1, description="Current page number (1-indexed)")
    page_size: int = Field(..., ge=1, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total available pages")
    items: List[T] = Field(..., description="List of items on current page")
