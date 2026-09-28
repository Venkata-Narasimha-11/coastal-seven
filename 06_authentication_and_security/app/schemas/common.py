"""Common Pydantic Schemas for Generic Responses."""

from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Standard generic JSON response message."""
    message: str = Field(..., description="Status or acknowledgment message")


class HealthCheckResponse(BaseModel):
    """System health status response."""
    status: str
    database: str
    version: str


class PaginatedResponse(BaseModel, Generic[T]):
    """Standardized paginated envelope wrapping collections."""
    total: int = Field(..., description="Total count of matching records")
    page: int = Field(..., description="Current page number (1-indexed)")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of available pages")
    items: List[T] = Field(..., description="List of items on current page")
