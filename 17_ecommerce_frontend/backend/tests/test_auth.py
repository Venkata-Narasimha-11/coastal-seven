"""Comprehensive automated tests for authentication, registration, login, and JWT validation."""

import pytest
from fastapi.testclient import TestClient


def test_register_user_success(client: TestClient):
    """Test successful user registration."""
    payload = {
        "email": "newuser@example.com",
        "username": "newuser123",
        "full_name": "New User",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@example.com"
    assert data["username"] == "newuser123"
    assert data["role"] == "customer"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_register_duplicate_email(client: TestClient, customer_user):
    """Test registration rejection when email already exists."""
    payload = {
        "email": customer_user.email,
        "username": "differentusername",
        "full_name": "Duplicate User",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "email address already exists" in response.json()["detail"]


def test_register_duplicate_username(client: TestClient, customer_user):
    """Test registration rejection when username is already taken."""
    payload = {
        "email": "differentemail@example.com",
        "username": customer_user.username,
        "full_name": "Duplicate User",
        "password": "Password123!",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 400
    assert "username is already taken" in response.json()["detail"]


def test_register_short_password(client: TestClient):
    """Test registration validation failure when password is too short."""
    payload = {
        "email": "shortpw@example.com",
        "username": "shortuser",
        "full_name": "Short Password",
        "password": "short",
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 422


def test_login_success(client: TestClient, customer_user):
    """Test successful login with username."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": customer_user.username, "password": "SecretPassword123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_email(client: TestClient, customer_user):
    """Test successful login using email instead of username."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": customer_user.email, "password": "SecretPassword123!"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_password(client: TestClient, customer_user):
    """Test login rejection on incorrect password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": customer_user.username, "password": "WrongPassword999!"},
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_get_current_user_me(client: TestClient, customer_token_headers, customer_user):
    """Test retrieving authenticated user profile using Bearer token."""
    response = client.get("/api/v1/auth/me", headers=customer_token_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == customer_user.email
    assert data["username"] == customer_user.username


def test_unauthenticated_request_rejected(client: TestClient):
    """Test that protected endpoint rejects requests without Bearer token."""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_update_profile(client: TestClient, customer_token_headers):
    """Test updating authenticated user profile."""
    update_data = {
        "full_name": "Johnathan Updated",
    }
    response = client.put("/api/v1/auth/me", json=update_data, headers=customer_token_headers)
    assert response.status_code == 200
    assert response.json()["full_name"] == "Johnathan Updated"
