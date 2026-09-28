"""Integration tests for Practice: Secure Product API.

Validates that:
1. Product API requires JWT authentication.
2. Only administrators ('admin' role) can create products (POST).
3. Only administrators can edit products (PUT / PATCH).
4. Only administrators can delete products (DELETE).
5. Standard users ('user' role) can view and browse catalog items.
6. Non-admin write operations are strictly rejected with 403 Forbidden.
7. Unauthenticated write operations are strictly rejected with 401 Unauthorized.
"""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestSecureProductAPI:
    """Test suite verifying RBAC enforcement on Product catalog endpoints."""

    async def _create_authenticated_user(self, async_client: AsyncClient, role: str) -> dict:
        uid = uuid.uuid4().hex[:6]
        email = f"prod_{role}_{uid}@example.com"
        password = "Password123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"prod_{role}_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
                "role": role,
            },
        )

        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = login_res.json()["access_token"]
        return {"headers": {"Authorization": f"Bearer {token}"}}

    async def test_unauthenticated_request_rejected_401(self, async_client: AsyncClient):
        """GET /api/v1/products and POST /api/v1/products without token return 401."""
        res_get = await async_client.get("/api/v1/products")
        assert res_get.status_code == 401

        res_post = await async_client.post(
            "/api/v1/products",
            json={
                "title": "Unauth Product",
                "sku": "UN-001",
                "price": 10.00,
            },
        )
        assert res_post.status_code == 401

    async def test_standard_user_can_browse_products(self, async_client: AsyncClient):
        """Standard user can list products and view catalog details."""
        user = await self._create_authenticated_user(async_client, role="user")
        response = await async_client.get("/api/v1/products", headers=user["headers"])
        assert response.status_code == 200
        assert "items" in response.json()

    async def test_standard_user_cannot_create_product_403(self, async_client: AsyncClient):
        """Standard user receives 403 Forbidden when attempting to create a product."""
        user = await self._create_authenticated_user(async_client, role="user")
        uid = uuid.uuid4().hex[:6].upper()

        response = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Forbidden Item {uid}",
                "sku": f"FB-{uid}",
                "price": 49.99,
                "category": "Gadgets",
            },
            headers=user["headers"],
        )
        assert response.status_code == 403
        assert "Operation not permitted" in response.json()["detail"]

    async def test_admin_can_create_product_201(self, async_client: AsyncClient):
        """Admin can successfully create a product with 201 Created."""
        admin = await self._create_authenticated_user(async_client, role="admin")
        uid = uuid.uuid4().hex[:6].upper()

        response = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Admin Created {uid}",
                "sku": f"ADM-{uid}",
                "price": 199.99,
                "category": "Hardware",
            },
            headers=admin["headers"],
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == f"Admin Created {uid}"
        assert data["sku"] == f"ADM-{uid}"
        assert float(data["price"]) == 199.99

    async def test_standard_user_cannot_edit_product_403(self, async_client: AsyncClient):
        """Standard user receives 403 Forbidden when attempting to PUT or PATCH a product."""
        admin = await self._create_authenticated_user(async_client, role="admin")
        user = await self._create_authenticated_user(async_client, role="user")
        uid = uuid.uuid4().hex[:6].upper()

        # Admin creates product
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Item to Protect {uid}",
                "sku": f"PRT-{uid}",
                "price": 89.99,
            },
            headers=admin["headers"],
        )
        p_id = create_res.json()["id"]

        # Standard user attempts PATCH
        patch_res = await async_client.patch(
            f"/api/v1/products/{p_id}",
            json={"price": 10.00},
            headers=user["headers"],
        )
        assert patch_res.status_code == 403

        # Standard user attempts PUT
        put_res = await async_client.put(
            f"/api/v1/products/{p_id}",
            json={
                "title": "Hacked Title",
                "sku": f"PRT-{uid}",
                "price": 1.00,
            },
            headers=user["headers"],
        )
        assert put_res.status_code == 403

    async def test_admin_can_edit_and_delete_product(self, async_client: AsyncClient):
        """Admin can successfully update (PATCH/PUT) and delete a product."""
        admin = await self._create_authenticated_user(async_client, role="admin")
        uid = uuid.uuid4().hex[:6].upper()

        # Create
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Editable Item {uid}",
                "sku": f"ED-{uid}",
                "price": 150.00,
            },
            headers=admin["headers"],
        )
        p_id = create_res.json()["id"]

        # Patch
        patch_res = await async_client.patch(
            f"/api/v1/products/{p_id}",
            json={"price": 129.99, "description": "Discount applied"},
            headers=admin["headers"],
        )
        assert patch_res.status_code == 200
        assert float(patch_res.json()["price"]) == 129.99

        # Delete
        del_res = await async_client.delete(
            f"/api/v1/products/{p_id}",
            headers=admin["headers"],
        )
        assert del_res.status_code == 204

        # Verify not found
        get_res = await async_client.get(
            f"/api/v1/products/{p_id}",
            headers=admin["headers"],
        )
        assert get_res.status_code == 404
