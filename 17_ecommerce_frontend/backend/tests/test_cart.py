"""Comprehensive automated tests for Redis-backed shopping cart operations."""

import pytest
from fastapi.testclient import TestClient
from app.models.product import Product


def test_view_empty_cart(client: TestClient, customer_token_headers):
    """Test retrieving an empty cart."""
    response = client.get("/api/v1/cart", headers=customer_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total_items"] == 0
    assert float(data["total_amount"]) == 0.0


def test_add_to_cart_success(client: TestClient, customer_token_headers, sample_product: Product):
    """Test successfully adding an in-stock product to the cart."""
    payload = {"product_id": sample_product.id, "quantity": 2}
    response = client.post("/api/v1/cart/items", json=payload, headers=customer_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total_items"] == 2
    assert len(data["items"]) == 1
    assert data["items"][0]["product_id"] == sample_product.id
    assert data["items"][0]["quantity"] == 2
    expected_total = float(sample_product.price) * 2
    assert float(data["total_amount"]) == pytest.approx(expected_total)


def test_add_to_cart_exceeds_stock(client: TestClient, customer_token_headers, sample_product: Product):
    """Test adding more items than available stock is rejected."""
    payload = {"product_id": sample_product.id, "quantity": sample_product.stock + 5}
    response = client.post("/api/v1/cart/items", json=payload, headers=customer_token_headers)
    assert response.status_code == 400
    assert "exceeds available inventory" in response.json()["detail"]


def test_add_to_cart_increments_existing(client: TestClient, customer_token_headers, sample_product: Product):
    """Test adding the same product again increments quantity correctly."""
    client.post("/api/v1/cart/items", json={"product_id": sample_product.id, "quantity": 1}, headers=customer_token_headers)
    response = client.post("/api/v1/cart/items", json={"product_id": sample_product.id, "quantity": 2}, headers=customer_token_headers)
    assert response.status_code == 200
    assert response.json()["total_items"] == 3


def test_update_cart_quantity(client: TestClient, customer_token_headers, sample_product: Product):
    """Test updating the quantity of an item in the cart."""
    client.post("/api/v1/cart/items", json={"product_id": sample_product.id, "quantity": 2}, headers=customer_token_headers)
    response = client.put(
        f"/api/v1/cart/items/{sample_product.id}",
        json={"quantity": 4},
        headers=customer_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["total_items"] == 4


def test_remove_item_from_cart(client: TestClient, customer_token_headers, sample_product: Product):
    """Test removing a specific product from the cart."""
    client.post("/api/v1/cart/items", json={"product_id": sample_product.id, "quantity": 2}, headers=customer_token_headers)
    response = client.delete(f"/api/v1/cart/items/{sample_product.id}", headers=customer_token_headers)
    assert response.status_code == 200
    assert response.json()["total_items"] == 0
    assert len(response.json()["items"]) == 0


def test_clear_cart(client: TestClient, customer_token_headers, sample_product: Product):
    """Test purging all items from the cart."""
    client.post("/api/v1/cart/items", json={"product_id": sample_product.id, "quantity": 2}, headers=customer_token_headers)
    response = client.delete("/api/v1/cart", headers=customer_token_headers)
    assert response.status_code == 204

    # Confirm cart is empty
    check = client.get("/api/v1/cart", headers=customer_token_headers)
    assert check.json()["total_items"] == 0
