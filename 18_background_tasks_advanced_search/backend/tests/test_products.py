"""Comprehensive automated tests for categories, product catalog CRUD, and Redis caching."""

import pytest
from fastapi.testclient import TestClient
from app.models.product import Category, Product


def test_list_categories(client: TestClient, sample_category: Category):
    """Test retrieving categories and verify response caching."""
    response = client.get("/api/v1/products/categories")
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 1
    assert any(c["name"] == sample_category.name for c in categories)


def test_create_category_admin(client: TestClient, admin_token_headers):
    """Test category creation by admin."""
    payload = {"name": "Home Appliances", "description": "Kitchen and cleaning appliances"}
    response = client.post("/api/v1/products/categories", json=payload, headers=admin_token_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Home Appliances"
    assert response.json()["slug"] == "home-appliances"


def test_create_category_forbidden_for_customer(client: TestClient, customer_token_headers):
    """Test that standard customers cannot create categories."""
    payload = {"name": "Books", "description": "Physical and e-books"}
    response = client.post("/api/v1/products/categories", json=payload, headers=customer_token_headers)
    assert response.status_code == 403


def test_create_product_admin(client: TestClient, admin_token_headers, sample_category):
    """Test product creation by admin."""
    payload = {
        "name": "Smart 4K Television",
        "description": "55-inch OLED display with HDR10+",
        "price": 799.99,
        "stock": 15,
        "category_id": sample_category.id,
    }
    response = client.post("/api/v1/products", json=payload, headers=admin_token_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Smart 4K Television"
    assert float(data["price"]) == 799.99
    assert data["stock"] == 15


def test_create_product_forbidden_for_customer(client: TestClient, customer_token_headers, sample_category):
    """Test that customer cannot create products."""
    payload = {
        "name": "Unauthorized Product",
        "price": 49.99,
        "stock": 5,
        "category_id": sample_category.id,
    }
    response = client.post("/api/v1/products", json=payload, headers=customer_token_headers)
    assert response.status_code == 403


def test_list_products_with_filter_and_search(client: TestClient, sample_product: Product):
    """Test catalog listing with pagination, search, and category filtering."""
    response = client.get("/api/v1/products?page=1&size=10&search=Headphones")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1
    assert any("Headphones" in item["name"] for item in data["items"])


def test_get_product_by_id_success(client: TestClient, sample_product: Product):
    """Test retrieving product detail by ID."""
    response = client.get(f"/api/v1/products/{sample_product.id}")
    assert response.status_code == 200
    assert response.json()["id"] == sample_product.id
    assert response.json()["name"] == sample_product.name


def test_get_product_not_found(client: TestClient):
    """Test 404 response for non-existent product."""
    response = client.get("/api/v1/products/99999")
    assert response.status_code == 404


def test_update_product_admin(client: TestClient, admin_token_headers, sample_product: Product):
    """Test updating product price and inventory by admin."""
    payload = {"price": 179.99, "stock": 25}
    response = client.put(f"/api/v1/products/{sample_product.id}", json=payload, headers=admin_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["price"]) == 179.99
    assert data["stock"] == 25


def test_delete_product_admin(client: TestClient, admin_token_headers, sample_product: Product):
    """Test product deletion by admin."""
    response = client.delete(f"/api/v1/products/{sample_product.id}", headers=admin_token_headers)
    assert response.status_code == 204

    # Verify deleted
    get_res = client.get(f"/api/v1/products/{sample_product.id}")
    assert get_res.status_code == 404
