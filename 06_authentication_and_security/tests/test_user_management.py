"""Integration tests for User management and administration under RBAC."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestUserManagement:
    """Test suite covering user CRUD operations protected by RBAC."""

    async def _create_user(self, async_client: AsyncClient, role: str) -> dict:
        uid = uuid.uuid4().hex[:6]
        email = f"mgmt_{role}_{uid}@example.com"
        password = "Password123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"mgmt_{role}_{uid}",
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
        return {"headers": {"Authorization": f"Bearer {token}"}, "email": email}

    async def test_admin_create_user_success(self, async_client: AsyncClient):
        """Admin can directly create user accounts via POST /api/v1/users."""
        admin = await self._create_user(async_client, role="admin")
        uid = uuid.uuid4().hex[:6]

        response = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"created_{uid}",
                "email": f"created_{uid}@example.com",
                "password": "CreatedPass123!",
                "confirm_password": "CreatedPass123!",
                "role": "user",
            },
            headers=admin["headers"],
        )
        assert response.status_code == 201
        assert response.json()["username"] == f"created_{uid}"

    async def test_standard_user_cannot_create_users_via_admin_endpoint(
        self, async_client: AsyncClient
    ):
        """Standard user cannot use POST /api/v1/users (403 Forbidden)."""
        user = await self._create_user(async_client, role="user")
        uid = uuid.uuid4().hex[:6]

        response = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"hacker_{uid}",
                "email": f"hacker_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            headers=user["headers"],
        )
        assert response.status_code == 403

    async def test_admin_can_delete_user(self, async_client: AsyncClient):
        """Admin can delete a user account via DELETE /api/v1/users/{id}."""
        admin = await self._create_user(async_client, role="admin")
        uid = uuid.uuid4().hex[:6]

        create_res = await async_client.post(
            "/api/v1/users",
            json={
                "username": f"del_{uid}",
                "email": f"del_{uid}@example.com",
                "password": "Password123!",
                "confirm_password": "Password123!",
            },
            headers=admin["headers"],
        )
        target_id = create_res.json()["id"]

        del_res = await async_client.delete(
            f"/api/v1/users/{target_id}",
            headers=admin["headers"],
        )
        assert del_res.status_code == 204
