"""Unit and integration tests for Authentication endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """Test standard user registration."""
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "full_name": "New User",
        "role": "developer",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert data["role"] == "developer"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_duplicate_username_fails(client: AsyncClient, seed_users):
    """Test registration fails when username is already taken."""
    payload = {
        "username": "admin_user",
        "email": "unique@example.com",
        "password": "Password123!",
        "full_name": "Another Admin",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    data = response.json()
    assert data["error"]["code"] == "DUPLICATE_ENTITY"


@pytest.mark.asyncio
async def test_register_duplicate_email_fails(client: AsyncClient, seed_users):
    """Test registration fails when email is already registered."""
    payload = {
        "username": "unique_username",
        "email": "admin@test.io",
        "password": "Password123!",
        "full_name": "Another User",
    }
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "DUPLICATE_ENTITY"


@pytest.mark.asyncio
async def test_login_json_success(client: AsyncClient, seed_users):
    """Test authentication via JSON credentials payload."""
    payload = {"username": "admin_user", "password": "Password123!"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_password_fails(client: AsyncClient, seed_users):
    """Test authentication rejection with incorrect password."""
    payload = {"username": "admin_user", "password": "WrongPassword!"}
    response = await client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.asyncio
async def test_login_form_oauth2_success(client: AsyncClient, seed_users):
    """Test OAuth2 standard form login used by Swagger UI."""
    data = {"username": "manager_user", "password": "Password123!"}
    response = await client.post("/api/v1/auth/token", data=data)
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_refresh_token_rotation(client: AsyncClient, seed_users):
    """Test token refresh workflow returning new tokens."""
    login_res = await client.post(
        "/api/v1/auth/login",
        json={"username": "developer_user", "password": "Password123!"},
    )
    refresh_token = login_res.json()["refresh_token"]

    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refresh_res.status_code == 200
    data = refresh_res.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_get_current_user_me(client: AsyncClient, auth_tokens):
    """Test retrieval of current user profile with valid Bearer token."""
    response = await client.get("/api/v1/auth/me", headers=auth_tokens["admin"])
    assert response.status_code == 200
    assert response.json()["username"] == "admin_user"
    assert response.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_unauthenticated_request_rejected(client: AsyncClient):
    """Test that requests lacking Bearer token receive 401 Unauthorized."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code == 401
