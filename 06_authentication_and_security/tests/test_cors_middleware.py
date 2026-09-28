"""Integration tests verifying FastAPI CORS middleware behavior."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestCORSMiddleware:
    """Test suite covering CORS headers and cross-origin preflight requests."""

    async def test_cors_preflight_allowed_origin(self, async_client: AsyncClient):
        """OPTIONS preflight from allowed origin returns Access-Control headers."""
        headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        }
        response = await async_client.options("/api/v1/auth/login", headers=headers)
        assert response.status_code == 200
        assert response.headers.get("access-control-allow-origin") == "http://localhost:3000"
        assert "POST" in response.headers.get("access-control-allow-methods", "")

    async def test_cors_disallowed_origin_not_reflected(self, async_client: AsyncClient):
        """Request from disallowed origin does not mirror back the access-control-allow-origin header."""
        headers = {
            "Origin": "http://malicious-site.evil.com",
            "Access-Control-Request-Method": "POST",
        }
        response = await async_client.options("/api/v1/auth/login", headers=headers)
        # CORS middleware does not add access-control-allow-origin for untrusted origins
        assert response.headers.get("access-control-allow-origin") != "http://malicious-site.evil.com"
