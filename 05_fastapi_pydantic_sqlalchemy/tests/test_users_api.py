"""Integration tests for FastAPI User CRUD endpoints."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserAPI:
    """Test suite for /api/v1/users endpoints."""

    async def test_create_user_success(self, async_client: AsyncClient):
        """POST /api/v1/users registers a new user with 201 Created."""
        uid = uuid.uuid4().hex[:8]
        payload = {
            "username": f"user_{uid}",
            "email": f"user_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "full_name": "API New User",
        }
        response = await async_client.post("/api/v1/users", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["id"] is not None
        assert data["username"] == f"user_{uid}"
        assert data["email"] == f"user_{uid}@example.com"
        assert "password" not in data
        assert "hashed_password" not in data

    async def test_create_user_password_mismatch_422(self, async_client: AsyncClient):
        """POST /api/v1/users with mismatched passwords returns 422 Unprocessable Entity."""
        uid = uuid.uuid4().hex[:8]
        payload = {
            "username": f"mismatch_{uid}",
            "email": f"mismatch_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "MismatchPassword456!",
        }
        response = await async_client.post("/api/v1/users", json=payload)
        assert response.status_code == 422

    async def test_create_user_duplicate_email_409(self, async_client: AsyncClient):
        """POST /api/v1/users returns 409 Conflict when email already exists."""
        uid = uuid.uuid4().hex[:8]
        # Create first
        first_payload = {
            "username": f"first_{uid}",
            "email": f"dup_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        r1 = await async_client.post("/api/v1/users", json=first_payload)
        assert r1.status_code == 201

        # Try duplicate
        dup_payload = {
            "username": f"second_{uid}",
            "email": f"dup_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        response = await async_client.post("/api/v1/users", json=dup_payload)
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]

    async def test_list_users_paginated(self, async_client: AsyncClient):
        """GET /api/v1/users returns PaginatedResponse structure."""
        response = await async_client.get("/api/v1/users?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "page" in data
        assert "items" in data
        assert len(data["items"]) <= 2

    async def test_get_user_by_id_success(self, async_client: AsyncClient):
        """GET /api/v1/users/{user_id} returns user with nested products."""
        # Create user with product first to ensure isolation
        uid = uuid.uuid4().hex[:8]
        u_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"owner_{uid}",
                "email": f"owner_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        assert u_res.status_code == 201
        u_id = u_res.json()["id"]

        response = await async_client.get(f"/api/v1/users/{u_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == u_id
        assert data["username"] == f"owner_{uid}"
        assert "products" in data
        assert isinstance(data["products"], list)

    async def test_get_user_not_found_404(self, async_client: AsyncClient):
        """GET /api/v1/users/99999 returns 404 Not Found."""
        response = await async_client.get("/api/v1/users/99999")
        assert response.status_code == 404

    async def test_update_user_success(self, async_client: AsyncClient):
        """PUT /api/v1/users/{user_id} updates user full_name."""
        uid = uuid.uuid4().hex[:8]
        u_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"upd_{uid}",
                "email": f"upd_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
                "full_name": "Before Update",
            },
        )
        u_id = u_res.json()["id"]

        payload = {"full_name": "After Update"}
        response = await async_client.put(f"/api/v1/users/{u_id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "After Update"

    async def test_delete_user_and_cascade(self, async_client: AsyncClient):
        """DELETE /api/v1/users/{user_id} returns 204 and removes user."""
        uid = uuid.uuid4().hex[:8]
        # 1. Create a user to delete
        create_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"del_{uid}",
                "email": f"del_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
        )
        assert create_res.status_code == 201
        del_user_id = create_res.json()["id"]

        # 2. Delete user
        del_res = await async_client.delete(f"/api/v1/users/{del_user_id}")
        assert del_res.status_code == 204

        # 3. Confirm 404 on fetch
        get_res = await async_client.get(f"/api/v1/users/{del_user_id}")
        assert get_res.status_code == 404
