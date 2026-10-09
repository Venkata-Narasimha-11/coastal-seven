"""Pydantic V2 schemas for order processing and tracking."""

from datetime import datetime
from decimal import Decimal
from typing import List
from pydantic import BaseModel, Field, ConfigDict
from app.models.order import OrderStatus


class OrderItemResponse(BaseModel):
    """Schema for item within an order."""
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    subtotal: Decimal

    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Schema for placing an order from the user's current Redis cart."""
    shipping_address: str = Field(..., min_length=5, max_length=500)


class OrderStatusUpdate(BaseModel):
    """Schema for updating an order's status."""
    status: OrderStatus


class OrderResponse(BaseModel):
    """Full order response schema."""
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatus
    shipping_address: str
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    model_config = ConfigDict(from_attributes=True)
