import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.database import Base, SessionLocal, engine
from app.models import Category, Product, User, UserRole
from app.utils.auth import get_password_hash


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Seed Users
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@ecommerce.io",
                full_name="Store Administrator",
                hashed_password=get_password_hash("AdminPassword123!"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            db.add(admin)

        customer = db.query(User).filter(User.username == "customer1").first()
        if not customer:
            customer = User(
                username="customer1",
                email="customer1@example.com",
                full_name="John Customer",
                hashed_password=get_password_hash("SecretPassword123!"),
                role=UserRole.CUSTOMER,
                is_active=True,
            )
            db.add(customer)

        db.commit()

        # 2. Seed Categories
        categories_data = [
            {"name": "Audio", "slug": "audio", "description": "Headphones, speakers, and ear buds"},
            {"name": "Wearables", "slug": "wearables", "description": "Smart watches, fitness trackers"},
            {"name": "Peripherals", "slug": "peripherals", "description": "Keyboards, mice, and monitors"},
            {"name": "Accessories", "slug": "accessories", "description": "Chargers, cables, and adapters"},
        ]

        cat_map = {}
        for cdata in categories_data:
            cat = db.query(Category).filter(Category.slug == cdata["slug"]).first()
            if not cat:
                cat = Category(**cdata)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            cat_map[cdata["slug"]] = cat

        # 3. Seed Products
        products_data = [
            {
                "name": "Sony WH-1000XM5 Wireless Headphones",
                "slug": "sony-wh1000xm5-wireless-headphones",
                "description": "Industry-leading noise canceling with two processors and 8 microphones.",
                "price": Decimal("349.99"),
                "stock": 15,
                "category_id": cat_map["audio"].id,
                "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Apple Watch Series 9 GPS 45mm",
                "slug": "apple-watch-series-9-gps-45mm",
                "description": "Advanced health sensors, Double Tap gesture, and brighter display.",
                "price": Decimal("399.00"),
                "stock": 12,
                "category_id": cat_map["wearables"].id,
                "image_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "RGB Mechanical Gaming Keyboard",
                "slug": "rgb-mechanical-gaming-keyboard",
                "description": "Hot-swappable switches, PBT double-shot keycaps, and aircraft aluminum frame.",
                "price": Decimal("129.50"),
                "stock": 25,
                "category_id": cat_map["peripherals"].id,
                "image_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Ultra-Wide 34-Inch Curved Gaming Monitor",
                "slug": "ultrawide-34-inch-curved-gaming-monitor",
                "description": "144Hz refresh rate, 1ms response time, and vibrant IPS panel.",
                "price": Decimal("549.99"),
                "stock": 8,
                "category_id": cat_map["peripherals"].id,
                "image_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Ergonomic Precision Wireless Mouse",
                "slug": "ergonomic-precision-wireless-mouse",
                "description": "Hyper-fast scroll wheel, 4000 DPI sensor, and rechargeable battery.",
                "price": Decimal("59.99"),
                "stock": 35,
                "category_id": cat_map["peripherals"].id,
                "image_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "100W GaN 4-Port Fast Charging Hub",
                "slug": "100w-gan-4-port-fast-charging-hub",
                "description": "Ultra-compact Gallium Nitride charger supporting laptops, phones, and tablets.",
                "price": Decimal("49.00"),
                "stock": 50,
                "category_id": cat_map["accessories"].id,
                "image_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80",
            },
        ]

        for pdata in products_data:
            prod = db.query(Product).filter(Product.slug == pdata["slug"]).first()
            if not prod:
                prod = Product(**pdata, is_active=True)
                db.add(prod)

        db.commit()
        print("Database successfully seeded with users, categories, and products!")

    except Exception as e:
        db.rollback()
        print("Seeding error:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed()
