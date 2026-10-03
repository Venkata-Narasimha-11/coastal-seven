import pytest


@pytest.mark.asyncio
async def test_sliding_window_rate_limiting_enforcement(client):
    # Strict limiter allows 3 requests per 10 seconds
    # Request 1: OK
    r1 = await client.get("/api/v1/rate-limit/strict")
    assert r1.status_code == 200
    assert r1.headers["X-RateLimit-Limit"] == "3"
    assert r1.headers["X-RateLimit-Remaining"] == "2"

    # Request 2: OK
    r2 = await client.get("/api/v1/rate-limit/strict")
    assert r2.status_code == 200
    assert r2.headers["X-RateLimit-Remaining"] == "1"

    # Request 3: OK
    r3 = await client.get("/api/v1/rate-limit/strict")
    assert r3.status_code == 200
    assert r3.headers["X-RateLimit-Remaining"] == "0"

    # Request 4: Over quota -> 429 Too Many Requests
    r4 = await client.get("/api/v1/rate-limit/strict")
    assert r4.status_code == 429
    assert "Retry-After" in r4.headers
    assert int(r4.headers["Retry-After"]) >= 1
    err_body = r4.json()
    assert err_body["detail"]["error"] == "Too Many Requests"


@pytest.mark.asyncio
async def test_standard_rate_limiter(client):
    # Standard limiter allows 5 requests
    res = await client.get("/api/v1/rate-limit/standard")
    assert res.status_code == 200
    assert res.headers["X-RateLimit-Limit"] == "5"
    assert int(res.headers["X-RateLimit-Remaining"]) >= 0
