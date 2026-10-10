"""Automated test suite for Day 19 API Security, Rate Limiting, and GZip Compression."""

import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.rate_limit import get_safe_client_ip, limiter


@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Reset rate limiter state before each test."""
    yield
    # Limiter reset logic if any storage keys exist
    try:
        limiter.reset()
    except Exception:
        pass


class TestSafeClientIPResolution:
    """Empirical verification of peer IP spoofing protection."""

    def test_untrusted_peer_ignores_forwarded_headers(self):
        """Untrusted client peer cannot spoof its IP address using X-Forwarded-For."""
        # Simulate connecting peer from untrusted external IP
        untrusted_client = TestClient(app, client=("198.51.100.5", 50000))
        response = untrusted_client.get(
            "/health",
            headers={"X-Forwarded-For": "10.0.0.1, 192.168.1.1"},
        )
        assert response.status_code == 200

        # Construct a dummy request matching untrusted peer
        class DummyRequest:
            class DummyClient:
                host = "198.51.100.5"
            client = DummyClient()
            headers = {"X-Forwarded-For": "10.0.0.1"}

        resolved_ip = get_safe_client_ip(DummyRequest())
        assert resolved_ip == "198.51.100.5", "Spoofed X-Forwarded-For must be ignored for untrusted peers"

    def test_trusted_peer_resolves_forwarded_ip(self):
        """Trusted reverse proxy (127.0.0.1) can safely forward real client IP."""
        class DummyRequest:
            class DummyClient:
                host = "127.0.0.1"
            client = DummyClient()
            headers = {"X-Forwarded-For": "203.0.113.195, 127.0.0.1"}

        resolved_ip = get_safe_client_ip(DummyRequest())
        assert resolved_ip == "203.0.113.195", "Origin IP from trusted proxy must be accurately extracted"


class TestRateLimiting:
    """Verification of SlowAPI rate limiting and HTTP 429 status enforcement."""

    def test_auth_login_rate_limiting(self, client):
        """POST /api/v1/auth/login throttles after 5 attempts per minute with HTTP 429."""
        payload = {"username": "nonexistent_user", "password": "WrongPassword123!"}

        # Make 5 allowed attempts (each returns 401 Unauthorized)
        for i in range(5):
            res = client.post("/api/v1/auth/login", json=payload)
            assert res.status_code == 401, f"Attempt {i+1} should return 401, got {res.status_code}"

        # 6th attempt must be blocked by rate limiter with HTTP 429
        blocked_res = client.post("/api/v1/auth/login", json=payload)
        assert blocked_res.status_code == 429, f"6th attempt must be 429, got {blocked_res.status_code}"
        json_data = blocked_res.json()
        assert "error" in json_data
        assert "Rate limit exceeded" in json_data["error"]

    def test_csv_import_rate_limiting(self, client, admin_token_headers):
        """POST /api/v1/tasks/products/import-csv throttles after 3 requests per minute."""
        for i in range(3):
            csv_content = f"name,price,category\nRate Limit Product {i},19.99,Electronics\n".encode()
            files = {"file": (f"test_{i}.csv", io.BytesIO(csv_content), "text/csv")}
            res = client.post(
                "/api/v1/tasks/products/import-csv",
                files=files,
                headers=admin_token_headers,
            )
            assert res.status_code in (200, 202), f"Attempt {i+1} should succeed, got {res.status_code}"

        # 4th attempt must be throttled
        csv_content = b"name,price,category\nRate Limit Product Blocked,19.99,Electronics\n"
        files = {"file": ("test_blocked.csv", io.BytesIO(csv_content), "text/csv")}
        blocked_res = client.post(
            "/api/v1/tasks/products/import-csv",
            files=files,
            headers=admin_token_headers,
        )
        assert blocked_res.status_code == 429, f"4th attempt must return 429, got {blocked_res.status_code}"


class TestResponseCompression:
    """Verification of GZipMiddleware threshold behavior."""

    def test_small_response_is_not_compressed(self, client):
        """Small response (< 1000 bytes) should not be GZipped."""
        res = client.get("/health", headers={"Accept-Encoding": "gzip"})
        assert res.status_code == 200
        assert "Content-Encoding" not in res.headers, "Small response under 1000B should not be compressed"
        assert len(res.content) < 1000

    def test_large_response_is_compressed(self, client, db, sample_category):
        """Large response (>= 1000 bytes) should include Content-Encoding: gzip."""
        from app.models.product import Product

        # Seed 15 products to ensure response body exceeds 1000 bytes
        for i in range(15):
            prod = Product(
                name=f"Compression Test Product {i}",
                slug=f"comp-product-{i}",
                description=f"Detailed description for compression benchmarking with sufficient payload {i}",
                price=29.99 + i,
                stock=50,
                category_id=sample_category.id,
                is_active=True,
            )
            db.add(prod)
        db.commit()

        res = client.get("/api/v1/products?size=20", headers={"Accept-Encoding": "gzip"})
        assert res.status_code == 200
        # Starlette GZipMiddleware sets Content-Encoding: gzip when response >= 1000 bytes
        assert res.headers.get("content-encoding") == "gzip", "Payload >= 1000B must be GZip compressed"
