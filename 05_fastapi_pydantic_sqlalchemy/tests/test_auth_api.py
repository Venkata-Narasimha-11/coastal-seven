"""Integration tests for Authentication (JWT Login & Profile) and PATCH operations."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    """Test suite for authentication and token validation."""

    async def test_login_success_and_get_me(self, async_client: AsyncClient):
        """POST /api/v1/auth/login issues JWT token, which authorizes GET /api/v1/auth/me."""
        uid = uuid.uuid4().hex[:8]
        email = f"auth_{uid}@example.com"
        password = "AuthPassword123!"

        # 1. Register a user
        reg_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"auth_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
                "full_name": "Auth Test User",
            },
        )
        assert reg_res.status_code == 201

        # 2. Login to get token
        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        token_data = login_res.json()
        assert "access_token" in token_data
        assert token_data["token_type"] == "bearer"
        access_token = token_data["access_token"]

        # 3. Access /auth/me with Bearer token
        headers = {"Authorization": f"Bearer {access_token}"}
        me_res = await async_client.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        user_info = me_res.json()
        assert user_info["email"] == email
        assert user_info["username"] == f"auth_{uid}"

    async def test_login_invalid_password_401(self, async_client: AsyncClient):
        """POST /api/v1/auth/login with wrong password returns 401 Unauthorized."""
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": "alice.admin@techstore.io", "password": "WrongPassword999!"},
        )
        assert response.status_code == 401

    async def test_get_me_unauthorized_without_token_401(self, async_client: AsyncClient):
        """GET /api/v1/auth/me without authorization header returns 401."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_patch_user_partial_update(self, async_client: AsyncClient):
        """PATCH /api/v1/users/{id} updates only provided fields."""
        uid = uuid.uuid4().hex[:8]
        reg_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"patch_{uid}",
                "email": f"patch_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Original Name",
            },
        )
        u_id = reg_res.json()["id"]

        patch_res = await async_client.patch(
            f"/api/v1/users/{u_id}",
            json={"full_name": "Patched Name Only"},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["full_name"] == "Patched Name Only"
        assert patch_res.json()["username"] == f"patch_{uid}"

    async def test_patch_product_partial_update(self, async_client: AsyncClient):
        """PATCH /api/v1/products/{id} updates only provided fields."""
        uid = uuid.uuid4().hex[:6].upper()
        create_res = await async_client.post(
            "/api/v1/products",
            json={
                "title": f"Patch Item {uid}",
                "sku": f"PT-{uid}",
                "price": 50.00,
                "category": "Testing",
                "owner_id": 2,
            },
        )
        p_id = create_res.json()["id"]

        patch_res = await async_client.patch(
            f"/api/v1/products/{p_id}",
            json={"price": 45.00},
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["price"] == 45.00
        assert patch_res.json()["title"] == f"Patch Item {uid}"
