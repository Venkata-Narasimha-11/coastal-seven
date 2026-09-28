"""Pydantic V2 Schemas for Product entity."""

from datetime import datetime
from typing import TYPE_CHECKING, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

if TYPE_CHECKING:
    from app.schemas.user import UserSummary


class ProductBase(BaseModel):
    """Base schema for Product attributes."""
    title: str = Field(
        ...,
        min_length=2,
        max_length=150,
        description="Product display title",
        examples=["Mechanical Keyboard"],
    )
    description: Optional[str] = Field(
        None,
        max_length=2000,
        description="Detailed product markdown or text description",
    )
    sku: str = Field(
        ...,
        pattern=r"^[A-Za-z0-9]{2,10}-[A-Za-z0-9]{2,10}$",
        description="Stock Keeping Unit (e.g., TECH-001, KB-RGB99)",
        examples=["KB-RGB99"],
    )
    price: float = Field(
        ...,
        gt=0.0,
        description="Retail listing price in USD (must be > 0.00)",
        examples=[129.99],
    )
    discount_price: Optional[float] = Field(
        None,
        gt=0.0,
        description="Discounted promotional price (must be less than price)",
        examples=[99.99],
    )
    stock_quantity: int = Field(
        0,
        ge=0,
        description="Quantity of stock physically available",
        examples=[50],
    )
    category: str = Field(
        "General",
        min_length=2,
        max_length=50,
        description="Category classification",
        examples=["Electronics"],
    )
    is_available: bool = Field(
        True,
        description="Availability status for public catalog display",
    )

    @field_validator("title", mode="before")
    @classmethod
    def clean_title(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v

    @field_validator("sku", mode="before")
    @classmethod
    def uppercase_sku(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @model_validator(mode="after")
    def validate_discount_less_than_price(self) -> "ProductBase":
        if self.discount_price is not None:
            if self.discount_price >= self.price:
                raise ValueError("discount_price must be strictly less than price")
        return self


class ProductCreate(ProductBase):
    """Schema for creating a new product."""
    owner_id: Optional[int] = Field(
        None,
        ge=1,
        description="User ID of the owning admin/user (defaults to authenticated admin)",
        examples=[1],
    )


class ProductUpdate(BaseModel):
    """Schema for updating an existing product (all fields optional)."""
    title: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None
    sku: Optional[str] = Field(None, pattern=r"^[A-Za-z0-9]{2,10}-[A-Za-z0-9]{2,10}$")
    price: Optional[float] = Field(None, gt=0.0)
    discount_price: Optional[float] = Field(None, gt=0.0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=2, max_length=50)
    is_available: Optional[bool] = None
    owner_id: Optional[int] = Field(None, ge=1)

    @field_validator("sku", mode="before")
    @classmethod
    def uppercase_update_sku(cls, v: Optional[str]) -> Optional[str]:
        if isinstance(v, str):
            return v.strip().upper()
        return v

    @model_validator(mode="after")
    def validate_discount_on_update(self) -> "ProductUpdate":
        if self.discount_price is not None and self.price is not None:
            if self.discount_price >= self.price:
                raise ValueError("discount_price must be strictly less than price")
        return self


class ProductSummary(BaseModel):
    """Lightweight product summary."""
    id: int
    title: str
    sku: str
    price: float
    is_available: bool

    model_config = ConfigDict(from_attributes=True)


class ProductResponse(ProductBase):
    """Full product response schema."""
    id: int = Field(..., description="Unique product identifier")
    owner_id: int = Field(..., description="Owner user ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    model_config = ConfigDict(from_attributes=True)


class ProductDetailResponse(ProductResponse):
    """Product response including nested owner information."""
    owner: "UserSummary" = Field(..., description="Summary details of product owner")

    model_config = ConfigDict(from_attributes=True)
