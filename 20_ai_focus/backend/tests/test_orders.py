"""Comprehensive automated tests for atomic order checkout, stock validation, and WebSocket order tracking."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.order import Order, OrderStatus
from app.models.product import Product
from app.models.user import User, UserRole
from app.utils.auth import create_access_token, get_password_hash


def test_checkout_empty_cart_fails(client: TestClient, customer_token_headers):
    """Test that checkout fails when shopping cart has no items."""
    payload = {"shipping_address": "123 Main St, Springfield, IL 62701"}
    response = client.post("/api/v1/orders/checkout", json=payload, headers=customer_token_headers)
    assert response.status_code == 400
    assert "empty shopping cart" in response.json()["detail"]


def test_checkout_success_and_stock_decremented(
    client: TestClient,
    customer_token_headers,
    sample_product: Product,
    db: Session,
):
    """Test atomic checkout decrements product stock and empties cart."""
    initial_stock = sample_product.stock
    buy_quantity = 3

    # Add item to cart
    client.post(
        "/api/v1/cart/items",
        json={"product_id": sample_product.id, "quantity": buy_quantity},
        headers=customer_token_headers,
    )

    # Perform checkout
    order_payload = {"shipping_address": "456 Oak Avenue, Metropolis, NY 10001"}
    response = client.post("/api/v1/orders/checkout", json=order_payload, headers=customer_token_headers)
    assert response.status_code == 201

    order_data = response.json()
    assert order_data["status"] == "pending"
    assert order_data["shipping_address"] == "456 Oak Avenue, Metropolis, NY 10001"
    assert len(order_data["items"]) == 1
    assert order_data["items"][0]["quantity"] == buy_quantity

    # Verify inventory was decremented in database
    db.refresh(sample_product)
    assert sample_product.stock == initial_stock - buy_quantity

    # Verify cart was cleared
    cart_res = client.get("/api/v1/cart", headers=customer_token_headers)
    assert cart_res.json()["total_items"] == 0


def test_checkout_stock_validation_prevents_overselling(
    client: TestClient,
    customer_token_headers,
    sample_product: Product,
    db: Session,
):
    """Test that atomic transaction blocks checkout and rolls back if stock drops below cart quantity."""
    # Put 4 items in cart
    client.post(
        "/api/v1/cart/items",
        json={"product_id": sample_product.id, "quantity": 4},
        headers=customer_token_headers,
    )

    # Simulate stock drop (e.g. another concurrent buyer bought all units)
    sample_product.stock = 2
    db.commit()

    # Attempt checkout
    order_payload = {"shipping_address": "789 Pine Road, Gotham, NJ 07001"}
    response = client.post("/api/v1/orders/checkout", json=order_payload, headers=customer_token_headers)
    assert response.status_code == 400
    assert "Insufficient stock" in response.json()["detail"]

    # Verify stock remained at 2 (no negative stock or partial decrement)
    prod = db.query(Product).filter(Product.id == sample_product.id).first()
    assert prod.stock == 2


def test_get_user_order_history(
    client: TestClient,
    customer_token_headers,
    sample_product: Product,
):
    """Test retrieving user's order history list."""
    # Place an order
    client.post(
        "/api/v1/cart/items",
        json={"product_id": sample_product.id, "quantity": 1},
        headers=customer_token_headers,
    )
    client.post(
        "/api/v1/orders/checkout",
        json={"shipping_address": "100 Bayview St, Seattle, WA"},
        headers=customer_token_headers,
    )

    response = client.get("/api/v1/orders", headers=customer_token_headers)
    assert response.status_code == 200
    orders = response.json()
    assert len(orders) >= 1
    assert "total_amount" in orders[0]


def test_get_order_by_id_forbidden_for_other_user(
    client: TestClient,
    customer_token_headers,
    sample_product: Product,
    db: Session,
):
    """Test that customer cannot view orders belonging to another user."""
    # Place order as customer
    client.post(
        "/api/v1/cart/items",
        json={"product_id": sample_product.id, "quantity": 1},
        headers=customer_token_headers,
    )
    order_res = client.post(
        "/api/v1/orders/checkout",
        json={"shipping_address": "100 Bayview St, Seattle, WA"},
        headers=customer_token_headers,
    )
    order_id = order_res.json()["id"]

    # Create another distinct customer
    other_user = User(
        email="other@example.com",
        username="otheruser",
        hashed_password=get_password_hash("OtherSecret123!"),
        role=UserRole.CUSTOMER,
        is_active=True,
    )
    db.add(other_user)
    db.commit()
    other_token = create_access_token(data={"sub": other_user.username, "role": other_user.role.value})
    other_headers = {"Authorization": f"Bearer {other_token}"}

    # Attempt to view first customer's order
    response = client.get(f"/api/v1/orders/{order_id}", headers=other_headers)
    assert response.status_code == 403


def test_admin_update_order_status(
    client: TestClient,
    customer_token_headers,
    admin_token_headers,
    sample_product: Product,
):
    """Test admin updating order lifecycle status from pending to confirmed."""
    client.post(
        "/api/v1/cart/items",
        json={"product_id": sample_product.id, "quantity": 1},
        headers=customer_token_headers,
    )
    order_res = client.post(
        "/api/v1/orders/checkout",
        json={"shipping_address": "100 Bayview St, Seattle, WA"},
        headers=customer_token_headers,
    )
    order_id = order_res.json()["id"]

    # Admin updates status to confirmed
    update_res = client.put(
        f"/api/v1/orders/{order_id}/status",
        json={"status": "confirmed"},
        headers=admin_token_headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "confirmed"


def test_websocket_order_tracking(client: TestClient):
    """Test full-duplex WebSocket connection to live order tracking channel."""
    with client.websocket_connect("/ws/orders/123") as websocket:
        initial_msg = websocket.receive_json()
        assert initial_msg["event"] == "CONNECTED"
        assert initial_msg["order_id"] == 123

        # Test heartbeat ping-pong
        websocket.send_text("ping")
        response = websocket.receive_text()
        assert response == "pong"
