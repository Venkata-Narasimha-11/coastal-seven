"""Integration tests for FastAPI Product Catalog CRUD and search endpoints."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestProductAPI:
    """Test suite for /api/v1/products endpoints."""

    async def test_create_product_success(self, async_client: AsyncClient):
        """POST /api/v1/products creates product linked to owner with 201 Created."""
        uid = uuid.uuid4().hex[:6].upper()
        payload = {
            "title": "Ergonomic Desk Mat",
            "description": "Premium leather desk mat with anti-slip base.",
            "sku": f"DM-{uid}",
            "price": 29.99,
            "discount_price": 24.99,
            "stock_quantity": 80,
            "category": "Accessories",
            "is_available": True,
            "owner_id": 2,  # seller_bob
        }
        response = await async_client.post("/api/v1/products", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["sku"] == f"DM-{uid}"
        assert data["owner_id"] == 2
        assert data["price"] == 29.99

    async def test_create_product_invalid_owner_400(self, async_client: AsyncClient):
        """POST /api/v1/products with non-existent owner returns 400 Bad Request."""
        payload = {
            "title": "Ghost Product",
            "sku": "GHO-0001",
            "price": 19.99,
            "category": "Misc",
            "owner_id": 99999,
        }
        response = await async_client.post("/api/v1/products", json=payload)
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]

    async def test_create_product_duplicate_sku_409(self, async_client: AsyncClient):
        """POST /api/v1/products with duplicated SKU returns 409 Conflict."""
        uid = uuid.uuid4().hex[:6].upper()
        # Create first product
        p1 = {
            "title": "First Monitor",
            "sku": f"MN-{uid}",
            "price": 299.99,
            "category": "Electronics",
            "owner_id": 2,
        }
        r1 = await async_client.post("/api/v1/products", json=p1)
        assert r1.status_code == 201

        # Attempt duplicate SKU
        p2 = {
            "title": "Second Monitor",
            "sku": f"MN-{uid}",
            "price": 399.99,
            "category": "Electronics",
            "owner_id": 2,
        }
        response = await async_client.post("/api/v1/products", json=p2)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_create_product_invalid_discount_422(self, async_client: AsyncClient):
        """POST /api/v1/products with discount >= price triggers Pydantic V2 validation error (422)."""
        payload = {
            "title": "Invalid Discount Item",
            "sku": "BAD-DSC01",
            "price": 50.00,
            "discount_price": 55.00,  # Invalid: discount > price
            "category": "Misc",
            "owner_id": 2,
        }
        response = await async_client.post("/api/v1/products", json=payload)
        assert response.status_code == 422

    async def test_list_products_and_filters(self, async_client: AsyncClient):
        """GET /api/v1/products supports search, category, and price range filters."""
        # 1. Category filter
        books_res = await async_client.get("/api/v1/products?category=Books")
        assert books_res.status_code == 200
        books_data = books_res.json()
        assert books_data["total"] >= 1
        assert all(item["category"] == "Books" for item in books_data["items"])

        # 2. Search query filter
        search_res = await async_client.get("/api/v1/products?search=Clean")
        assert search_res.status_code == 200
        search_data = search_res.json()
        assert search_data["total"] >= 1
        assert any("Clean" in item["title"] for item in search_data["items"])

        # 3. Price range filter
        price_res = await async_client.get("/api/v1/products?min_price=10&max_price=600")
        assert price_res.status_code == 200
        price_data = price_res.json()
        assert all(10 <= item["price"] <= 600 for item in price_data["items"])

    async def test_get_product_by_id_with_owner(self, async_client: AsyncClient):
        """GET /api/v1/products/{product_id} returns product with nested owner profile."""
        uid = uuid.uuid4().hex[:6].upper()
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Owner Test Item {uid}",
                "sku": f"OWN-{uid}",
                "price": 75.00,
                "category": "Testing",
                "owner_id": 2,
            },
        )
        assert create_res.status_code == 201
        pid = create_res.json()["id"]

        response = await async_client.get(f"/api/v1/products/{pid}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == pid
        assert "owner" in data
        assert data["owner"]["username"] == "seller_bob"

    async def test_update_product_success(self, async_client: AsyncClient):
        """PUT /api/v1/products/{product_id} updates price and stock."""
        uid = uuid.uuid4().hex[:6].upper()
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Update Test Item {uid}",
                "sku": f"UPD-{uid}",
                "price": 100.00,
                "stock_quantity": 10,
                "category": "Testing",
                "owner_id": 2,
            },
        )
        assert create_res.status_code == 201
        pid = create_res.json()["id"]

        payload = {
            "price": 120.00,
            "stock_quantity": 25,
        }
        response = await async_client.put(f"/api/v1/products/{pid}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["price"] == 120.00
        assert data["stock_quantity"] == 25

    async def test_delete_product_success(self, async_client: AsyncClient):
        """DELETE /api/v1/products/{product_id} returns 204 and removes product."""
        uid = uuid.uuid4().hex[:6].upper()
        # 1. Create product to delete
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": "Temporary Product",
                "sku": f"DEL-{uid}",
                "price": 10.00,
                "category": "Temp",
                "owner_id": 2,
            },
        )
        assert create_res.status_code == 201
        prod_id = create_res.json()["id"]

        # 2. Delete product
        del_res = await async_client.delete(f"/api/v1/products/{prod_id}")
        assert del_res.status_code == 204

        # 3. Verify 404
        get_res = await async_client.get(f"/api/v1/products/{prod_id}")
        assert get_res.status_code == 404
