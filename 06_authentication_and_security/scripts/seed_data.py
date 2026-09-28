"""Database Seeding Script for Day 6: Authentication & Security."""

import asyncio
from decimal import Decimal
import logging
import sys
from pathlib import Path

# Configure utf-8 encoding for Windows terminals
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.security import get_password_hash
from app.db.base import Base
from app.db.session import AsyncSessionLocal, async_engine
from app.models.product import Product
from app.models.user import User, UserRole

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("SeedData")

SAMPLE_USERS = [
    {
        "username": "admin_alice",
        "email": "admin@techstore.io",
        "password": "AdminPass123!",
        "full_name": "Alice Administrator",
        "role": UserRole.ADMIN.value,
        "is_superuser": True,
        "is_active": True,
    },
    {
        "username": "user_bob",
        "email": "customer@techstore.io",
        "password": "UserPass123!",
        "full_name": "Bob Customer",
        "role": UserRole.USER.value,
        "is_superuser": False,
        "is_active": True,
    },
    {
        "username": "inactive_charlie",
        "email": "charlie.inactive@techstore.io",
        "password": "CharliePass123!",
        "full_name": "Charlie Inactive",
        "role": UserRole.USER.value,
        "is_superuser": False,
        "is_active": False,
    },
]

SAMPLE_PRODUCTS = [
    {
        "title": "Quantum Mechanical Keyboard",
        "description": "Custom aluminum 75% mechanical keyboard with hot-swappable tactile switches and RGB backlighting.",
        "sku": "KB-Q75PRO",
        "price": Decimal("189.99"),
        "discount_price": Decimal("159.99"),
        "stock_quantity": 45,
        "category": "Peripherals",
        "is_available": True,
    },
    {
        "title": "Ergonomic Vertical Mouse",
        "description": "Wireless ergonomic mouse with 4000 DPI optical sensor and dual Bluetooth/2.4G connectivity.",
        "sku": "MS-ERG500",
        "price": 69.95,
        "discount_price": 54.95,
        "stock_quantity": 120,
        "category": "Peripherals",
        "is_available": True,
    },
    {
        "title": "Ultra-Wide 34-Inch Curved Monitor",
        "description": "WQHD 3440x1440 144Hz curved gaming and productivity monitor with HDR400.",
        "sku": "MN-UW34C",
        "price": 549.00,
        "discount_price": 489.00,
        "stock_quantity": 18,
        "category": "Displays",
        "is_available": True,
    },
    {
        "title": "Noise-Cancelling Studio Headphones",
        "description": "Closed-back studio reference headphones with active hybrid noise cancellation and 40mm drivers.",
        "sku": "AU-NC400",
        "price": 249.99,
        "discount_price": None,
        "stock_quantity": 30,
        "category": "Audio",
        "is_available": True,
    },
]


async def seed_database() -> None:
    """Populate database with initial admin, standard user, and sample products."""
    logger.info("Verifying database schema...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        created_users = {}

        # 1. Seed Users
        from sqlalchemy import or_, select

        for user_data in SAMPLE_USERS:
            existing = await session.scalar(
                select(User).where(
                    or_(
                        User.email == user_data["email"],
                        User.username == user_data["username"],
                    )
                )
            )
            if not existing:
                user = User(
                    username=user_data["username"],
                    email=user_data["email"],
                    hashed_password=get_password_hash(user_data["password"]),
                    full_name=user_data["full_name"],
                    role=user_data["role"],
                    is_superuser=user_data["is_superuser"],
                    is_active=user_data["is_active"],
                )
                session.add(user)
                await session.flush()
                await session.refresh(user)
                created_users[user.role] = user
                logger.info("Seeded User: %s (role: %s, email: %s)", user.username, user.role, user.email)
            else:
                created_users[existing.role] = existing
                logger.info("User already exists: %s (%s)", existing.username, existing.email)

        # 2. Seed Products (owned by Admin)
        admin_user = created_users.get(UserRole.ADMIN.value)
        if admin_user:
            for prod_data in SAMPLE_PRODUCTS:
                existing_p = await session.scalar(
                    select(Product).where(Product.sku == prod_data["sku"])
                )
                if not existing_p:
                    product = Product(
                        title=prod_data["title"],
                        description=prod_data["description"],
                        sku=prod_data["sku"],
                        price=prod_data["price"],
                        discount_price=prod_data["discount_price"],
                        stock_quantity=prod_data["stock_quantity"],
                        category=prod_data["category"],
                        is_available=prod_data["is_available"],
                        owner_id=admin_user.id,
                    )
                    session.add(product)
                    logger.info("Seeded Product: %s (SKU: %s)", product.title, product.sku)

        await session.commit()
        logger.info("✅ Database seeding complete!")


if __name__ == "__main__":
    asyncio.run(seed_database())
