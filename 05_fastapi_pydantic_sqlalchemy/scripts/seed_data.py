"""Seed script to populate initial sample users and catalog products."""

import asyncio
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import hash_password
from app.db.session import AsyncSessionLocal, async_engine
from app.models.product import Product
from app.models.user import User
from sqlalchemy import select


SAMPLE_USERS = [
    {
        "username": "admin_alice",
        "email": "alice.admin@techstore.io",
        "password": "AdminPassword123!",
        "full_name": "Alice Admin",
        "is_active": True,
        "is_superuser": True,
    },
    {
        "username": "seller_bob",
        "email": "bob.seller@gadgets.com",
        "password": "SellerPassword123!",
        "full_name": "Bob Merchant",
        "is_active": True,
        "is_superuser": False,
    },
    {
        "username": "seller_charlie",
        "email": "charlie.books@readmore.org",
        "password": "BooksPassword123!",
        "full_name": "Charlie Bookseller",
        "is_active": True,
        "is_superuser": False,
    },
    {
        "username": "inactive_dave",
        "email": "dave.inactive@oldmail.com",
        "password": "InactivePass123!",
        "full_name": "Dave Inactive",
        "is_active": False,
        "is_superuser": False,
    },
]

SAMPLE_PRODUCTS = [
    {
        "owner_username": "seller_bob",
        "title": "UltraHD 4K Curved Gaming Monitor",
        "description": "34-inch 144Hz 1ms curved gaming monitor with HDR400 and USB-C hub.",
        "sku": "TECH-MN01",
        "price": 499.99,
        "discount_price": 449.99,
        "stock_quantity": 25,
        "category": "Electronics",
        "is_available": True,
    },
    {
        "owner_username": "seller_bob",
        "title": "Ergonomic Mechanical Keyboard",
        "description": "Hot-swappable mechanical switches, RGB backlighting, aircraft aluminum frame.",
        "sku": "TECH-KB02",
        "price": 129.50,
        "discount_price": 99.99,
        "stock_quantity": 60,
        "category": "Electronics",
        "is_available": True,
    },
    {
        "owner_username": "seller_bob",
        "title": "Wireless Precision Mouse",
        "description": "Ergonomic wireless mouse with 20000 DPI optical sensor and fast charging.",
        "sku": "TECH-MS03",
        "price": 69.99,
        "discount_price": None,
        "stock_quantity": 110,
        "category": "Electronics",
        "is_available": True,
    },
    {
        "owner_username": "seller_charlie",
        "title": "Clean Code: A Handbook of Agile Software Craftsmanship",
        "description": "Classic textbook on writing readable, reusable, and maintainable software.",
        "sku": "BOOK-CC01",
        "price": 42.00,
        "discount_price": 35.50,
        "stock_quantity": 40,
        "category": "Books",
        "is_available": True,
    },
    {
        "owner_username": "seller_charlie",
        "title": "Designing Data-Intensive Applications",
        "description": "The definitive guide to distributed systems, transactions, and data architecture.",
        "sku": "BOOK-DDIA",
        "price": 55.00,
        "discount_price": 48.00,
        "stock_quantity": 30,
        "category": "Books",
        "is_available": True,
    },
    {
        "owner_username": "seller_charlie",
        "title": "Python Distilled",
        "description": "An essential guide to practical modern Python 3.8+ programming by David Beazley.",
        "sku": "BOOK-PY03",
        "price": 38.99,
        "discount_price": None,
        "stock_quantity": 15,
        "category": "Books",
        "is_available": True,
    },
    {
        "owner_username": "seller_bob",
        "title": "Vintage Mechanical Keyboard (Archived)",
        "description": "Discontinued vintage mechanical keyboard collector item.",
        "sku": "TECH-VINT",
        "price": 250.00,
        "discount_price": None,
        "stock_quantity": 0,
        "category": "Electronics",
        "is_available": False,
    },
]


async def seed_database() -> None:
    """Async function to insert initial seed data into PostgreSQL."""
    print("[*] Connecting to database to seed initial data...")
    user_map = {}

    async with AsyncSessionLocal() as session:
        # 1. Insert Users
        for user_data in SAMPLE_USERS:
            stmt = select(User).where(User.username == user_data["username"])
            result = await session.execute(stmt)
            existing = result.scalars().first()

            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=hash_password(user_data["password"]),
                    full_name=user_data["full_name"],
                    is_active=user_data["is_active"],
                    is_superuser=user_data["is_superuser"],
                )
                session.add(user)
                await session.flush()
                await session.refresh(user)
                print(f"  [+] Created User: {user.username} (ID: {user.id})")
                user_map[user.username] = user
            else:
                print(f"  [-] User already exists: {existing.username} (ID: {existing.id})")
                user_map[existing.username] = existing

        # 2. Insert Products
        for prod_data in SAMPLE_PRODUCTS:
            stmt = select(Product).where(Product.sku == prod_data["sku"])
            result = await session.execute(stmt)
            existing_prod = result.scalars().first()

            if not existing_prod:
                owner = user_map.get(prod_data["owner_username"])
                if not owner:
                    print(f"  [!] Owner {prod_data['owner_username']} not found. Skipping product.")
                    continue

                prod = Product(
                    title=prod_data["title"],
                    description=prod_data["description"],
                    sku=prod_data["sku"],
                    price=prod_data["price"],
                    discount_price=prod_data["discount_price"],
                    stock_quantity=prod_data["stock_quantity"],
                    category=prod_data["category"],
                    is_available=prod_data["is_available"],
                    owner_id=owner.id,
                )
                session.add(prod)
                await session.flush()
                await session.refresh(prod)
                print(f"  [+] Created Product: {prod.title} (SKU: {prod.sku}, Owner: {owner.username})")
            else:
                print(f"  [-] Product already exists: {existing_prod.sku}")

        await session.commit()
    print("[OK] Database seeding completed successfully!")


if __name__ == "__main__":
    asyncio.run(seed_database())
