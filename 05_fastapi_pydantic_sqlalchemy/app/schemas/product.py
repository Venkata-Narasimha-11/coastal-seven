"""Pydantic V2 Schemas for Product entity."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.schemas.user import UserDetailResponse, UserSummary


class ProductBase(BaseModel):
    """Base product schema with validation rules."""
    title: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Name or title of the product",
        examples=["Wireless Noise-Canceling Headphones"],
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Comprehensive product description",
        examples=["Premium over-ear headphones with 30-hour battery life."],
    )
    sku: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]{2,10}-[A-Za-z0-9]{2,10}$",
        description="Standard Stock Keeping Unit format (e.g. TECH-001, KB-001)",
        examples=["TECH-001"],
    )
    price: float = Field(
        ...,
        gt=0,
        description="Base retail price in USD (must be strictly greater than 0)",
        examples=[199.99],
    )
    discount_price: Optional[float] = Field(
        None,
        gt=0,
        description="Optional promotional sale price (must be lower than regular price)",
        examples=[149.99],
    )
    stock_quantity: int = Field(
        0,
        ge=0,
        description="Available inventory stock count (non-negative)",
        examples=[50],
    )
    category: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Department or product category",
        examples=["Electronics"],
    )
    is_available: bool = Field(
        True,
        description="Whether this product is currently listed for sale",
    )

    @field_validator("sku", mode="before")
    @classmethod
    def normalize_sku(cls, v: str) -> str:
        """Field validator: transform SKU to uppercase and strip whitespace."""
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @field_validator("price", "discount_price")
    @classmethod
    def round_prices(cls, v: Optional[float]) -> Optional[float]:
        """Field validator: round currency amounts to 2 decimal places."""
        if v is not None:
            return round(v, 2)
        return v

    @model_validator(mode="after")
    def validate_discount_less_than_price(self) -> "ProductBase":
        """Model validator: ensure discount_price is strictly less than price."""
        if self.discount_price is not None and self.discount_price >= self.price:
            raise ValueError(
                f"Discount price ({self.discount_price}) must be strictly less than base price ({self.price})"
            )
        return self


class ProductCreate(ProductBase):
    """Schema for registering a new product under an owner."""
    owner_id: int = Field(
        ...,
        ge=1,
        description="The ID of the user who owns/manages this product",
        examples=[1],
    )


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)."""
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = Field(None, max_length=2000)
    sku: Optional[str] = Field(None, pattern=r"^[A-Za-z0-9]{2,10}-[A-Za-z0-9]{2,10}$")
    price: Optional[float] = Field(None, gt=0)
    discount_price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    is_available: Optional[bool] = None

    @field_validator("sku", mode="before")
    @classmethod
    def normalize_update_sku(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @field_validator("price", "discount_price")
    @classmethod
    def round_update_prices(cls, v: Optional[float]) -> Optional[float]:
        if v is not None:
            return round(v, 2)
        return v

    @model_validator(mode="after")
    def validate_update_discounts(self) -> "ProductUpdate":
        """Validate discount price logic when both are provided in update payload."""
        if self.price is not None and self.discount_price is not None:
            if self.discount_price >= self.price:
                raise ValueError("discount_price must be strictly less than price")
        return self


class ProductSummary(BaseModel):
    """Lightweight product summary schema for embedding into User responses."""
    id: int = Field(..., description="Unique product identifier")
    title: str = Field(..., description="Product title")
    sku: str = Field(..., description="Stock Keeping Unit")
    price: float = Field(..., description="Base price")
    discount_price: Optional[float] = None
    category: str = Field(..., description="Product category")
    is_available: bool = Field(..., description="Available status")

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Standard API response schema for product queries."""
    id: int = Field(..., description="Unique product identifier")
    owner_id: int = Field(..., description="User ID of the product owner")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last modification timestamp")

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductResponse):
    """Detailed product response schema including nested Owner details."""
    owner: Optional[UserSummary] = Field(
        None,
        description="Profile details of the user who owns this product",
    )

    model_config = ConfigDict(from_attributes=True)


# Rebuild UserDetailResponse to resolve the forward reference to ProductSummary
UserDetailResponse.model_rebuild()
