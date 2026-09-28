"""Integration tests covering OAuth2 password specification flow and OAuth2PasswordBearer."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestOAuth2Flow:
    """Test suite covering standard OAuth2 flow with form URL-encoded login."""

    async def test_oauth2_token_form_login_success(self, async_client: AsyncClient):
        """POST /api/v1/auth/token with application/x-www-form-urlencoded succeeds."""
        uid = uuid.uuid4().hex[:6]
        email = f"oauth_{uid}@example.com"
        password = "OAuthPassword123!"

        # Register user
        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"oauth_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        # Standard OAuth2 form request
        form_payload = {
            "username": email,
            "password": password,
        }
        response = await async_client.post(
            "/api/v1/auth/token",
            data=form_payload,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_oauth2_form_login_on_login_endpoint(self, async_client: AsyncClient):
        """POST /api/v1/auth/login also accepts application/x-www-form-urlencoded data."""
        uid = uuid.uuid4().hex[:6]
        email = f"form_{uid}@example.com"
        password = "FormPassword123!"

        await async_client.post(
            "/api/v1/auth/register",
            json={
                "username": f"form_{uid}",
                "email": email,
                "password": password,
                "confirm_password": password,
            },
        )

        response = await async_client.post(
            "/api/v1/auth/login",
            data={"username": email, "password": password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        assert response.status_code == 200
        assert "access_token" in response.json()

    async def test_oauth2_www_authenticate_header_on_401(self, async_client: AsyncClient):
        """Unauthenticated request to protected route returns WWW-Authenticate: Bearer."""
        response = await async_client.get("/api/v1/auth/me")
        assert response.status_code == 401
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "Bearer"
