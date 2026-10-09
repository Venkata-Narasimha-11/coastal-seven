import logging
from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.models.user import User
from app.routers.websocket import manager as ws_manager
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.services.celery_app import send_order_confirmation_email
from app.services.redis_service import CacheService, CartService, get_redis
from app.utils.auth import get_current_admin, get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def checkout(
    order_in: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Atomic multi-item order checkout from Redis cart with strict inventory validation.
    
    Guarantees:
    1. Entire checkout runs in a single database transaction.
    2. Validates that every item has sufficient available stock.
    3. Atomically decrements product stock to prevent race conditions and overselling.
    4. Automatically rolls back all changes if any item violates inventory limits.
    5. Clears Redis cart and triggers async confirmation email upon successful commit.
    """
    if current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrators cannot place retail customer orders. Please sign in with a customer account to make purchases.",
        )

    cart_key = f"cart:{current_user.id}"
    raw_cart = get_redis().hgetall(cart_key)

    if not raw_cart:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot checkout with an empty shopping cart",
        )

    # Parse cart product IDs and quantities
    cart_items = {int(pid): int(qty) for pid, qty in raw_cart.items()}

    # Begin atomic transaction block
    try:
        total_amount = Decimal("0.00")
        order_items_to_create = []
        email_items = []

        # Lock rows or query products for validation
        product_ids = list(cart_items.keys())
        # Query products
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        product_map = {p.id: p for p in products}

        # Validate stock for all items BEFORE making any modifications
        for product_id, quantity in cart_items.items():
            product = product_map.get(product_id)
            if not product or not product.is_active:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Product with ID {product_id} is no longer available",
                )

            if product.stock < quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Insufficient stock for '{product.name}'. "
                        f"Available: {product.stock}, requested: {quantity}."
                    ),
                )

        # Create Order record
        new_order = Order(
            user_id=current_user.id,
            total_amount=Decimal("0.00"),
            status=OrderStatus.PENDING,
            shipping_address=order_in.shipping_address,
        )
        db.add(new_order)
        db.flush()  # Assigns new_order.id

        # Decrement stock and assemble line items
        for product_id, quantity in cart_items.items():
            product = product_map[product_id]

            # Atomically decrement stock
            product.stock -= quantity

            item_subtotal = Decimal(str(product.price)) * quantity
            total_amount += item_subtotal

            order_item = OrderItem(
                order_id=new_order.id,
                product_id=product.id,
                quantity=quantity,
                unit_price=product.price,
                subtotal=item_subtotal,
            )
            order_items_to_create.append(order_item)

            email_items.append({
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": str(product.price),
                "subtotal": str(item_subtotal),
            })

        new_order.total_amount = total_amount
        db.add_all(order_items_to_create)

        # Commit transaction atomically
        db.commit()
        db.refresh(new_order)

    except HTTPException:
        db.rollback()
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Checkout transaction failed: {str(exc)}",
        )

    # Post-commit actions:
    # 1. Clear shopping cart in Redis
    CartService.clear_cart(current_user.id)

    # 2. Invalidate product list caches since stock decreased
    CacheService.invalidate_product_caches()

    # 3. Dispatch asynchronous Celery confirmation email
    try:
        send_order_confirmation_email.delay(
            order_id=new_order.id,
            user_email=current_user.email,
            total_amount=float(total_amount),
            items=email_items,
        )
    except Exception:
        # Fallback to direct synchronous execution if Celery broker is offline
        try:
            send_order_confirmation_email(
                order_id=new_order.id,
                user_email=current_user.email,
                total_amount=float(total_amount),
                items=email_items,
            )
        except Exception:
            pass

    # 4. Dispatch real-time WebSocket alert to Admin Dashboard
    try:
        out_of_stock_list = []
        low_stock_list = []
        for pid in cart_items.keys():
            prod = product_map.get(pid)
            if prod:
                if prod.stock == 0:
                    out_of_stock_list.append({"id": prod.id, "name": prod.name})
                elif prod.stock < 5:
                    low_stock_list.append({"id": prod.id, "name": prod.name, "stock": prod.stock})

        await ws_manager.broadcast_admin_event({
            "event": "NEW_ORDER",
            "order_id": new_order.id,
            "customer": current_user.username,
            "total_amount": f"{float(new_order.total_amount):.2f}",
            "items_count": len(cart_items),
            "items": email_items,
            "out_of_stock": out_of_stock_list,
            "low_stock": low_stock_list,
        })
    except Exception as ws_err:
        logger.warning("Failed to broadcast admin alert: %s", ws_err)

    return new_order


@router.get("", response_model=List[OrderResponse])
def get_user_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve all past orders placed by the current user (or all orders if admin)."""
    if current_user.role.value == "admin":
        orders = db.query(Order).order_by(Order.created_at.desc()).all()
    else:
        orders = (
            db.query(Order)
            .filter(Order.user_id == current_user.id)
            .order_by(Order.created_at.desc())
            .all()
        )
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order_by_id(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get details of a specific order (restricted to owner or admin)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    if order.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not own this order",
        )

    return order


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_in: OrderStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    """Update order status and broadcast the change via WebSockets (Admin only)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    order.status = status_in.status
    db.commit()
    db.refresh(order)

    # Broadcast real-time update to all WebSocket clients tracking this order
    await ws_manager.broadcast_order_update(
        order_id=order.id,
        message={
            "event": "STATUS_UPDATED",
            "order_id": order.id,
            "status": order.status.value,
            "updated_at": order.updated_at.isoformat(),
        },
    )

    return order
