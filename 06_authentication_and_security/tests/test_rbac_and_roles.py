"""Integration tests for Role-Based Access Control (Admin vs User)."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestRBACAndRoles:
    """Test suite covering role enforcement and permissions."""

    async def _create_user(self, async_client: AsyncClient, role: str) -> dict:
        uid = uuid.uuid4().hex[:6]
        email = f"{role}_{uid}@example.com"
        password = "Password123!"

        reg_res = await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"{role}_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
                "role": role,
            },
        )
        assert reg_res.status_code == 201
        user_info = reg_res.json()

        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert login_res.status_code == 200
        token = login_res.json()["access_token"]

        return {
            "id": user_info["id"],
            "email": email,
            "role": role,
            "token": token,
            "headers": {"Authorization": f"Bearer {token}"},
        }

    async def test_standard_user_forbidden_from_admin_user_list(self, async_client: AsyncClient):
        """GET /api/v1/users is restricted to admins; standard user receives 403 Forbidden."""
        normal_user = await self._create_user(async_client, role="user")

        response = await async_client.get("/api/v1/users", headers=normal_user["headers"])
        assert response.status_code == 403
        assert "Operation not permitted" in response.json()["detail"]

    async def test_admin_user_allowed_to_list_users(self, async_client: AsyncClient):
        """GET /api/v1/users succeeds with 200 OK when requested by an admin."""
        admin_user = await self._create_user(async_client, role="admin")

        response = await async_client.get("/api/v1/users", headers=admin_user["headers"])
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert data["total"] >= 1

    async def test_standard_user_cannot_elevate_role(self, async_client: AsyncClient):
        """Standard user cannot change their own role to 'admin' via PATCH /api/v1/users/{id}."""
        normal_user = await self._create_user(async_client, role="user")

        response = await async_client.patch(
            f"/api/v1/users/{normal_user['id']}",
            json={"role": "admin"},
            headers=normal_user["headers"],
        )
        assert response.status_code == 403
        assert "Only administrators can modify account roles" in response.json()["detail"]

    async def test_standard_user_cannot_view_other_user_profile(self, async_client: AsyncClient):
        """Standard user receives 403 Forbidden when trying to view another user's profile."""
        user1 = await self._create_user(async_client, role="user")
        user2 = await self._create_user(async_client, role="user")

        response = await async_client.get(
            f"/api/v1/users/{user2['id']}",
            headers=user1["headers"],
        )
        assert response.status_code == 403
        assert "not authorized" in response.json()["detail"]

    async def test_admin_can_view_any_user_profile(self, async_client: AsyncClient):
        """Admin can view any user's profile without restriction."""
        normal_user = await self._create_user(async_client, role="user")
        admin_user = await self._create_user(async_client, role="admin")

        response = await async_client.get(
            f"/api/v1/users/{normal_user['id']}",
            headers=admin_user["headers"],
        )
        assert response.status_code == 200
        assert response.json()["id"] == normal_user["id"]
