"""Shopping Cart endpoints backed by high-speed in-memory Redis Hashes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.cart import AddToCartSchema, CartResponse, UpdateCartItemSchema
from app.services.redis_service import CartService
from app.utils.auth import get_current_user

router = APIRouter(prefix="/cart", tags=["Redis Shopping Cart"])


@router.get("", response_model=CartResponse)
def view_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all items currently stored in the authenticated user's Redis cart."""
    return CartService.get_cart(current_user.id, db)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_200_OK)
def add_to_cart(
    item_in: AddToCartSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Add a product or increment its quantity in the user's Redis shopping cart."""
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot add items to cart. Please use a customer account for shopping.",
        )
    try:
        return CartService.add_to_cart(
            user_id=current_user.id,
            product_id=item_in.product_id,
            quantity=item_in.quantity,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    product_id: int,
    item_in: UpdateCartItemSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update item quantity in cart. If quantity is 0, the item is removed."""
    try:
        return CartService.update_quantity(
            user_id=current_user.id,
            product_id=product_id,
            quantity=item_in.quantity,
            db=db,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    product_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Remove a product line item from the user's Redis cart."""
    CartService.remove_item(user_id=current_user.id, product_id=product_id)
    return CartService.get_cart(current_user.id, db)


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
):
    """Completely purge the user's cart from Redis."""
    CartService.clear_cart(current_user.id)
    return None
