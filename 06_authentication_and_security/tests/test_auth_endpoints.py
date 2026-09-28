"""Integration tests for Authentication endpoints: /register, /login, /me, /refresh."""

from datetime import timedelta
import uuid
import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, create_refresh_token


@pytest.mark.asyncio
class TestAuthEndpoints:
    """Test suite for authentication lifecycle endpoints."""

    async def test_register_success(self, async_client: AsyncClient):
        """POST /api/v1/auth/register creates a new user and returns 201."""
        uid = uuid.uuid4().hex[:6]
        payload = {
            "username": f"reg_{uid}",
            "email": f"reg_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
            "full_name": "Registered User",
            "role": "user",
        }
        response = await async_client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == f"reg_{uid}"
        assert data["email"] == f"reg_{uid}@example.com"
        assert data["role"] == "user"
        assert "hashed_password" not in data

    async def test_register_duplicate_email_409(self, async_client: AsyncClient):
        """POST /api/v1/auth/register returns 409 Conflict if email is taken."""
        uid = uuid.uuid4().hex[:6]
        payload = {
            "username": f"first_{uid}",
            "email": f"dup_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        res1 = await async_client.post("/api/v1/auth/register", json=payload)
        assert res1.status_code == 201

        # Second registration with same email but different username
        payload["username"] = f"second_{uid}"
        res2 = await async_client.post("/api/v1/auth/register", json=payload)
        assert res2.status_code == 409
        assert "already exists" in res2.json()["detail"]

    async def test_register_duplicate_username_409(self, async_client: AsyncClient):
        """POST /api/v1/auth/register returns 409 Conflict if username is taken."""
        uid = uuid.uuid4().hex[:6]
        payload = {
            "username": f"dupuser_{uid}",
            "email": f"first_{uid}@example.com",
            "password": "Password123!",
            "confirm_password": "Password123!",
        }
        res1 = await async_client.post("/api/v1/auth/register", json=payload)
        assert res1.status_code == 201

        # Second registration with same username but different email
        payload["email"] = f"second_{uid}@example.com"
        res2 = await async_client.post("/api/v1/auth/register", json=payload)
        assert res2.status_code == 409
        assert "already exists" in res2.json()["detail"]

    async def test_login_success_and_tokens_issued(self, async_client: AsyncClient):
        """POST /api/v1/auth/login issues valid access and refresh tokens."""
        uid = uuid.uuid4().hex[:6]
        email = f"login_{uid}@example.com"
        password = "LoginPass123!"

        # Register user
        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"login_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        # Login
        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert data["expires_in"] > 0

    async def test_login_invalid_password_401(self, async_client: AsyncClient):
        """POST /api/v1/auth/login returns 401 when given an incorrect password."""
        uid = uuid.uuid4().hex[:6]
        email = f"wrong_{uid}@example.com"
        password = "GoodPassword123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"wrong_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        response = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "WrongPassword999!"},
        )
        assert response.status_code == 401
        assert "Incorrect" in response.json()["detail"]

    async def test_get_me_success(self, async_client: AsyncClient):
        """GET /api/v1/auth/me returns current user details with valid token."""
        uid = uuid.uuid4().hex[:6]
        email = f"me_{uid}@example.com"
        password = "MePassword123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"me_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
                "full_name": "Self Tester",
            },
        )
        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        token = login_res.json()["access_token"]

        response = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == email
        assert data["username"] == f"me_{uid}"
        assert data["full_name"] == "Self Tester"

    async def test_get_me_unauthorized_without_token(self, async_client: AsyncClient):
        """GET /api/v1/auth/me returns 401 when no token is supplied."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401

    async def test_refresh_token_success(self, async_client: AsyncClient):
        """POST /api/v1/auth/refresh returns renewed access token and refresh token."""
        uid = uuid.uuid4().hex[:6]
        email = f"ref_{uid}@example.com"
        password = "RefPassword123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"ref_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )
        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        refresh_token = login_res.json()["refresh_token"]

        # Refresh
        ref_res = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )
        assert ref_res.status_code == 200
        ref_data = ref_res.json()
        assert "access_token" in ref_data
        assert "refresh_token" in ref_data

        # Verify new access token works for /me
        new_token = ref_data["access_token"]
        me_res = await async_client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {new_token}"},
        )
        assert me_res.status_code == 200
        assert me_res.json()["email"] == email

    async def test_refresh_rejects_access_token(self, async_client: AsyncClient):
        """POST /api/v1/auth/refresh rejects an access token passed as refresh token (401)."""
        uid = uuid.uuid4().hex[:6]
        email = f"acc_{uid}@example.com"
        password = "AccPassword123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"acc_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )
        login_res = await async_client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": password},
        )
        access_token = login_res.json()["access_token"]

        # Send access_token to /refresh
        ref_res = await async_client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": access_token},
        )
        assert ref_res.status_code == 401
