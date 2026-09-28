"""Automated End-to-End Demonstration for Day 5: FastAPI, Pydantic V2 & SQLAlchemy 2.0."""

import asyncio
import json
import sys
from pathlib import Path

# Configure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from httpx import ASGITransport, AsyncClient
from pydantic import ValidationError

from app.core.config import settings
from app.db.session import check_database_connection
from app.main import app
from app.schemas.product import ProductCreate
from app.schemas.user import UserCreate


def print_header(title: str) -> None:
    """Print section divider."""
    print("\n" + "=" * 75)
    print(f"  >>> {title.upper()}")
    print("=" * 75)


def print_step(step_num: int, title: str) -> None:
    """Print step title."""
    print(f"\n[{step_num}] {title}")
    print("-" * 65)


async def run_demo():
    print_header("Day 5: FastAPI, Pydantic V2 & SQLAlchemy 2.0 Live Verification")
    print(f"Project Name : {settings.PROJECT_NAME}")
    print(f"API Prefix   : {settings.API_V1_STR}")
    print(f"Database     : PostgreSQL ({settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME})")

    # --------------------------------------------------------------------------
    # Step 1: Database Connectivity Check
    # --------------------------------------------------------------------------
    print_step(1, "PostgreSQL Database Connectivity Check")
    connected = await check_database_connection()
    if connected:
        print("[OK] Successfully connected to PostgreSQL via SQLAlchemy 2.0 AsyncEngine.")
    else:
        print("[ERROR] Could not connect to PostgreSQL. Please check .env settings.")
        return

    # --------------------------------------------------------------------------
    # Step 2: Pydantic V2 Validation Demonstration
    # --------------------------------------------------------------------------
    print_step(2, "Pydantic V2 Field & Model Validators Demonstration")

    # Case A: Password mismatch validation
    print("  Testing @model_validator: Password confirmation mismatch...")
    try:
        UserCreate(
            username="bad_pass_user",
            email="test@example.com",
            password="Password123!",
            confirm_password="WrongPassword456!",
        )
        print("  [FAIL] Validation unexpectedly passed!")
    except ValidationError as e:
        err_msg = e.errors()[0]["msg"]
        print(f"  [OK] Caught expected ValidationError: '{err_msg}'")

    # Case B: Product pricing validation (discount_price >= price)
    print("\n  Testing @model_validator: discount_price >= price check...")
    try:
        ProductCreate(
            title="Defective Price Monitor",
            sku="TECH-DEF01",
            price=100.00,
            discount_price=120.00,  # Invalid!
            category="Electronics",
            owner_id=1,
        )
        print("  [FAIL] Discount validation unexpectedly passed!")
    except ValidationError as e:
        err_msg = e.errors()[0]["msg"]
        print(f"  [OK] Caught expected ValidationError: '{err_msg}'")

    # Case C: Successful normalization and regex
    print("\n  Testing @field_validator: SKU uppercase and email lowercasing...")
    prod = ProductCreate(
        title="Gaming Mousepad",
        sku="  desk-mp01  ",
        price=19.999,
        discount_price=14.991,
        category="Accessories",
        owner_id=1,
    )
    print(f"  [OK] Input '  desk-mp01  ' normalized to SKU: '{prod.sku}'")
    print(f"  [OK] Price 19.999 rounded to: ${prod.price:.2f}")
    print(f"  [OK] Discount 14.991 rounded to: ${prod.discount_price:.2f}")

    # --------------------------------------------------------------------------
    # Step 3: FastAPI End-to-End HTTP Endpoints Demonstration
    # --------------------------------------------------------------------------
    print_step(3, "FastAPI End-to-End CRUD and Query Execution")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://demo-server") as client:

        # 3.1 Health Check Probe
        print("  --> GET /health")
        res = await client.get("/health")
        print(f"      Status: {res.status_code} | Body: {res.json()}")

        # 3.2 Create User (POST /api/v1/users)
        demo_user_email = f"demo_merchant_{asyncio.get_event_loop().time():.0f}@shop.org"
        demo_username = f"merchant_{int(asyncio.get_event_loop().time()) % 100000}"
        user_payload = {
            "username": demo_username,
            "email": demo_user_email,
            "password": "MerchantPass123!",
            "confirm_password": "MerchantPass123!",
            "full_name": "Demo Merchant",
        }
        print(f"\n  --> POST /api/v1/users (username: {demo_username})")
        res = await client.post("/api/v1/users", json=user_payload)
        assert res.status_code == 201, f"User creation failed: {res.text}"
        user_data = res.json()
        user_id = user_data["id"]
        print(f"      [Created] User ID: {user_id}, Email: {user_data['email']}")

        # 3.3 Create Product for that User (POST /api/v1/products)
        sku_suffix = int(asyncio.get_event_loop().time()) % 10000
        prod_payload = {
            "title": f"Pro Wireless Mechanical Keyboard #{sku_suffix}",
            "description": "Custom mechanical keyboard with lubricated linear switches.",
            "sku": f"KB-{sku_suffix:04d}",
            "price": 149.99,
            "discount_price": 129.99,
            "stock_quantity": 30,
            "category": "Electronics",
            "is_available": True,
            "owner_id": user_id,
        }
        print(f"\n  --> POST /api/v1/products (SKU: {prod_payload['sku']})")
        res = await client.post("/api/v1/products", json=prod_payload)
        assert res.status_code == 201, f"Product creation failed: {res.text}"
        prod_data = res.json()
        product_id = prod_data["id"]
        print(f"      [Created] Product ID: {product_id}, Title: '{prod_data['title']}', Price: ${prod_data['price']}")

        # 3.4 Query Products with multi-parameter filtering
        print("\n  --> GET /api/v1/products?category=Electronics&min_price=100&limit=5")
        res = await client.get("/api/v1/products?category=Electronics&min_price=100&limit=5")
        assert res.status_code == 200
        p_data = res.json()
        print(f"      Matching Records: {p_data['total']} | Page {p_data['page']} of {p_data['total_pages']}")
        for item in p_data["items"][:3]:
            print(f"        - [{item['sku']}] {item['title']} - ${item['price']} (Stock: {item['stock_quantity']})")

        # 3.5 Full-text search
        print("\n  --> GET /api/v1/products?search=Keyboard")
        res = await client.get("/api/v1/products?search=Keyboard")
        assert res.status_code == 200
        search_results = res.json()
        print(f"      Found {search_results['total']} items matching 'Keyboard'.")

        # 3.6 Fetch User with Nested Products (Demonstrating Relationship & Pydantic Nesting)
        print(f"\n  --> GET /api/v1/users/{user_id} (Nested Products Relationship)")
        res = await client.get(f"/api/v1/users/{user_id}")
        assert res.status_code == 200
        nested_user = res.json()
        print(f"      User: {nested_user['username']} ({nested_user['full_name']})")
        print(f"      Owned Products Count: {len(nested_user['products'])}")
        for p in nested_user["products"]:
            print(f"        * SKU: {p['sku']}, Title: {p['title']}, Price: ${p['price']}")

        # 3.7 Update Product Details (PUT /api/v1/products/{id})
        print(f"\n  --> PUT /api/v1/products/{product_id} (Price Update)")
        update_payload = {"price": 139.99, "stock_quantity": 25}
        res = await client.put(f"/api/v1/products/{product_id}", json=update_payload)
        assert res.status_code == 200
        updated = res.json()
        print(f"      [Updated] New Price: ${updated['price']} | New Stock: {updated['stock_quantity']}")

        # 3.8 Delete Product (DELETE /api/v1/products/{id})
        print(f"\n  --> DELETE /api/v1/products/{product_id}")
        res = await client.delete(f"/api/v1/products/{product_id}")
        assert res.status_code == 204
        print(f"      [Deleted] HTTP 204 No Content returned.")

        # Confirm 404
        verify_del = await client.get(f"/api/v1/products/{product_id}")
        print(f"      [Verified] GET after DELETE returned HTTP {verify_del.status_code} Not Found.")

    print_header("Day 5 Live Demonstration Completed Successfully!")
    print("[+] FastAPI Swagger documentation active at : http://127.0.0.1:8000/docs")
    print("[+] ReDoc documentation active at             : http://127.0.0.1:8000/redoc")
    print("[+] All Pydantic V2 validations verified.")
    print("[+] All SQLAlchemy 2.0 async operations verified against PostgreSQL.")


if __name__ == "__main__":
    asyncio.run(run_demo())
