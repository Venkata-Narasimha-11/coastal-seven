"""Pydantic V2 schemas for product catalog and categories."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


# Category Schemas
class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    pass


class CategoryResponse(CategoryBase):
    id: int
    slug: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Product Schemas
class ProductBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0, decimal_places=2)
    stock: int = Field(..., ge=0)
    category_id: int
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0, decimal_places=2)
    stock: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: Optional[bool] = None


class ProductResponse(ProductBase):
    id: int
    slug: str
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    category: Optional[CategoryResponse] = None

    model_config = ConfigDict(from_attributes=True)


class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
