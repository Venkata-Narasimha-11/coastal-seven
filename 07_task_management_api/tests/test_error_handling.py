"""Unit and integration tests for Uniform Error Handling."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_error_404_standard_response(client: AsyncClient, auth_tokens):
    """Test 404 response payload structure."""
    response = await client.get("/api/v1/tasks/99999", headers=auth_tokens["admin"])
    assert response.status_code == 404
    data = response.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "99999" in data["error"]["message"]
    assert data["status_code"] == 404


@pytest.mark.asyncio
async def test_error_403_standard_response(client: AsyncClient, auth_tokens):
    """Test 403 forbidden error structure."""
    response = await client.post(
        "/api/v1/projects/",
        json={"name": "Forbidden Project"},
        headers=auth_tokens["viewer"],
    )
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "PERMISSION_DENIED"
    assert data["status_code"] == 403


@pytest.mark.asyncio
async def test_error_409_standard_response(client: AsyncClient, seed_users):
    """Test 409 conflict error structure."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "admin_user",
            "email": "unique_email@test.com",
            "password": "Password123!",
            "full_name": "Admin Duplicate",
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "DUPLICATE_ENTITY"
    assert data["status_code"] == 409


@pytest.mark.asyncio
async def test_error_422_standard_response(client: AsyncClient):
    """Test 422 validation error structure with field details."""
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "ok",  # Min length 3
            "email": "not-an-email",  # Invalid email
            "password": "12",  # Too short
            "full_name": "",  # Min length 2
        },
    )
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert isinstance(data["error"]["details"], list)
    assert len(data["error"]["details"]) >= 3
