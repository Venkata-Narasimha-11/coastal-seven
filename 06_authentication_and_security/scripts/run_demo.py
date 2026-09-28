"""Comprehensive Live Demonstration Script for Day 6: Authentication & Security.

Runs all 9 Day 6 core requirements end-to-end against the FastAPI application:
1. Password Security with passlib + bcrypt
2. JWT Token generation & decoding with python-jose
3. OAuth2 password authentication flow
4. Endpoints: /register, /login, /me, /refresh
5. User authentication dependency (Depends(get_current_user))
6. Role-Based Access Control (Admin vs User)
7. CORS middleware headers
8. Environment Configuration via pydantic-settings
9. Practice: Secured Product API with Admin-only write/edit/delete
"""

import asyncio
import json
import sys
import uuid
from pathlib import Path

# Configure utf-8 encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from httpx import ASGITransport, AsyncClient

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    decode_refresh_token,
    get_password_hash,
    verify_password,
)
from app.main import app


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(f"🔹 {title}")
    print("=" * 80)


async def main() -> None:
    print("=" * 80)
    print(f"🚀 DAY 6: AUTHENTICATION & SECURITY - LIVE DEMO WALKTHROUGH")
    print(f"📦 Project: {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"⚙️  Environment: {settings.ENVIRONMENT} | Algorithm: {settings.ALGORITHM}")
    print("=" * 80)

    # --------------------------------------------------------------------------
    # 1. Password Security (passlib + bcrypt)
    # --------------------------------------------------------------------------
    print_section("1. Password Security (passlib + bcrypt)")
    plain_password = "SuperSecret123!"
    hashed = get_password_hash(plain_password)
    print(f"Plain Password:   {plain_password}")
    print(f"Bcrypt Hash:      {hashed}")
    match = verify_password(plain_password, hashed)
    wrong_match = verify_password("WrongPassword123!", hashed)
    print(f"Verification of correct password: {match}  (Expected: True)")
    print(f"Verification of wrong password:   {wrong_match} (Expected: False)")
    assert match is True and wrong_match is False

    # --------------------------------------------------------------------------
    # 2. JWT Authentication (python-jose access & refresh tokens)
    # --------------------------------------------------------------------------
    print_section("2. JWT Authentication (python-jose)")
    sample_sub = 42
    access_tok = create_access_token(subject=sample_sub, roles=["admin"])
    refresh_tok = create_refresh_token(subject=sample_sub)
    print(f"Generated Access Token:  {access_tok[:45]}...")
    print(f"Generated Refresh Token: {refresh_tok[:45]}...")

    decoded_acc = decode_access_token(access_tok)
    decoded_ref = decode_refresh_token(refresh_tok)
    print(f"Decoded Access Token Claims:  {json.dumps(decoded_acc)}")
    print(f"Decoded Refresh Token Claims: {json.dumps(decoded_ref)}")
    assert decoded_acc["sub"] == str(sample_sub)
    assert decoded_acc["type"] == "access"
    assert decoded_ref["type"] == "refresh"

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:

        # ----------------------------------------------------------------------
        # 3. User Registration (/auth/register)
        # ----------------------------------------------------------------------
        print_section("3. User Registration (/api/v1/auth/register)")
        uid = uuid.uuid4().hex[:6]
        user_email = f"user_{uid}@example.com"
        user_pwd = "UserPass123!"

        reg_payload = {
            "username": f"user_{uid}",
            "email": user_email,
            "password": user_pwd,
            "confirm_password": user_pwd,
            "full_name": f"Regular User {uid}",
            "role": "user",
        }
        res_reg = await client.post("/api/v1/auth/register", json=reg_payload)
        print(f"Status: {res_reg.status_code}")
        print(f"Response: {res_reg.json()}")
        assert res_reg.status_code == 201
        created_user = res_reg.json()

        # ----------------------------------------------------------------------
        # 4. User Login & Token Generation (/auth/login)
        # ----------------------------------------------------------------------
        print_section("4. User Login (/api/v1/auth/login)")
        login_res = await client.post(
            "/api/v1/auth/login",
            json={"email": user_email, "password": user_pwd},
        )
        print(f"Status: {login_res.status_code}")
        token_data = login_res.json()
        print(f"Access Token:  {token_data['access_token'][:45]}...")
        print(f"Refresh Token: {token_data['refresh_token'][:45]}...")
        print(f"Expires In:    {token_data['expires_in']} seconds")
        assert login_res.status_code == 200
        user_access_token = token_data["access_token"]
        user_refresh_token = token_data["refresh_token"]

        # ----------------------------------------------------------------------
        # 5. User Profile Dependency (/auth/me with Bearer token)
        # ----------------------------------------------------------------------
        print_section("5. Current User Profile Dependency (/api/v1/auth/me)")
        headers_user = {"Authorization": f"Bearer {user_access_token}"}
        me_res = await client.get("/api/v1/auth/me", headers=headers_user)
        print(f"Status: {me_res.status_code}")
        print(f"Authenticated User Profile: {me_res.json()}")
        assert me_res.status_code == 200
        assert me_res.json()["email"] == user_email

        # ----------------------------------------------------------------------
        # 6. Token Refresh Flow (/auth/refresh)
        # ----------------------------------------------------------------------
        print_section("6. Token Refresh Flow (/api/v1/auth/refresh)")
        ref_res = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": user_refresh_token},
        )
        print(f"Status: {ref_res.status_code}")
        ref_data = ref_res.json()
        print(f"New Access Token:  {ref_data['access_token'][:45]}...")
        print(f"New Refresh Token: {ref_data['refresh_token'][:45]}...")
        assert ref_res.status_code == 200

        # ----------------------------------------------------------------------
        # 7. Role-Based Access Control: Regular User vs Admin on Product API
        # ----------------------------------------------------------------------
        print_section("7. Role-Based Access Control (Admin vs User on Product API)")

        # Attempting to create a product as a standard user -> MUST FAIL WITH 403 FORBIDDEN
        prod_payload = {
            "title": f"Unauthorized Item {uid}",
            "sku": f"PR-{uid.upper()}",
            "price": 99.99,
            "category": "Testing",
        }
        user_create_prod = await client.post(
            "/api/v1/products",
            json=prod_payload,
            headers=headers_user,
        )
        print(f"Regular User Product Creation Status: {user_create_prod.status_code} (Expected 403 Forbidden)")
        print(f"Response: {user_create_prod.json()}")
        assert user_create_prod.status_code == 403
        print("✅ RBAC successfully prevented standard user from creating products!")

        # ----------------------------------------------------------------------
        # 8. Admin Creation & Successful Product Management
        # ----------------------------------------------------------------------
        print_section("8. Admin Authentication & Successful Product Management")
        admin_email = f"admin_{uid}@example.com"
        admin_pwd = "AdminPass123!"
        admin_reg = await client.post(
            "/api/v1/auth/register",
            json={
                "username": f"admin_{uid}",
                "email": admin_email,
                "password": admin_pwd,
                "confirm_password": admin_pwd,
                "full_name": f"Admin User {uid}",
                "role": "admin",
            },
        )
        assert admin_reg.status_code == 201

        # Login as Admin
        admin_login = await client.post(
            "/api/v1/auth/login",
            json={"email": admin_email, "password": admin_pwd},
        )
        assert admin_login.status_code == 200
        admin_token = admin_login.json()["access_token"]
        headers_admin = {"Authorization": f"Bearer {admin_token}"}

        # Admin creating a product -> MUST SUCCEED WITH 201 CREATED
        admin_create_prod = await client.post(
            "/api/v1/products",
            json=prod_payload,
            headers=headers_admin,
        )
        print(f"Admin Product Creation Status: {admin_create_prod.status_code} (Expected 201 Created)")
        print(f"Created Product: {admin_create_prod.json()}")
        assert admin_create_prod.status_code == 201
        created_prod_id = admin_create_prod.json()["id"]

        # Admin editing product via PATCH -> MUST SUCCEED WITH 200 OK
        admin_patch_prod = await client.patch(
            f"/api/v1/products/{created_prod_id}",
            json={"price": 79.99, "description": "Updated by admin"},
            headers=headers_admin,
        )
        print(f"Admin Product Update Status: {admin_patch_prod.status_code} (Expected 200 OK)")
        print(f"Updated Product: {admin_patch_prod.json()}")
        assert admin_patch_prod.status_code == 200
        assert float(admin_patch_prod.json()["price"]) == 79.99

        # Regular user attempting to edit product -> MUST FAIL WITH 403
        user_patch_prod = await client.patch(
            f"/api/v1/products/{created_prod_id}",
            json={"price": 10.00},
            headers=headers_user,
        )
        print(f"Regular User Edit Attempt Status: {user_patch_prod.status_code} (Expected 403 Forbidden)")
        assert user_patch_prod.status_code == 403

        # ----------------------------------------------------------------------
        # 9. CORS Middleware Verification
        # ----------------------------------------------------------------------
        print_section("9. CORS Middleware Preflight Verification")
        cors_headers = {
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization,Content-Type",
        }
        options_res = await client.options("/api/v1/products", headers=cors_headers)
        print(f"OPTIONS Status: {options_res.status_code}")
        print(f"Access-Control-Allow-Origin: {options_res.headers.get('access-control-allow-origin')}")
        print(f"Access-Control-Allow-Methods: {options_res.headers.get('access-control-allow-methods')}")
        assert options_res.headers.get("access-control-allow-origin") == "http://localhost:3000"

    print("\n" + "=" * 80)
    print("🎉 ALL DAY 6 REQUIREMENTS & DEMOS PASSED SUCCESSFULLY!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
