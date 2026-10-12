"""Pydantic V2 schemas for Redis shopping cart."""

from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class AddToCartSchema(BaseModel):
    """Schema to add an item to the user's cart."""
    product_id: int
    quantity: int = Field(default=1, gt=0, description="Quantity must be greater than 0")


class UpdateCartItemSchema(BaseModel):
    """Schema to adjust quantity of a cart item."""
    quantity: int = Field(..., gt=0, description="New quantity must be greater than 0")


class CartItemResponse(BaseModel):
    """Representation of an item inside the user's cart."""
    product_id: int
    product_name: str
    unit_price: Decimal
    quantity: int
    subtotal: Decimal
    thumbnail_url: Optional[str] = None
    available_stock: int


class CartResponse(BaseModel):
    """Full shopping cart summary."""
    items: List[CartItemResponse]
    total_items: int
    total_amount: Decimal
