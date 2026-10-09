"""Setup PostgreSQL GIN indexes and seed test products for Day 18 Search & Celery tasks."""

import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import text
from app.database import SessionLocal, engine, Base
from app.models.product import Category, Product
from app.models.user import User, UserRole
from app.models.order import Order, OrderItem, OrderStatus


def setup_indexes_and_seed():
    print("1. Creating database tables if needed...")
    Base.metadata.create_all(bind=engine)

    print("2. Setting up PostgreSQL extensions & GIN indexes...")
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm;"))
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_products_fts 
                ON products USING gin(to_tsvector('english', name || ' ' || coalesce(description, '')));
                """
            )
        )
        conn.execute(
            text(
                """
                CREATE INDEX IF NOT EXISTS idx_products_trgm 
                ON products USING gin(name gin_trgm_ops);
                """
            )
        )
        conn.commit()
    print("   PostgreSQL GIN indexes successfully configured!")

    db = SessionLocal()
    try:
        # Check or create default category
        cat_electronics = db.query(Category).filter(Category.slug == "electronics").first()
        if not cat_electronics:
            cat_electronics = Category(
                name="Electronics",
                slug="electronics",
                description="Laptops, smartphones, audio and accessories",
            )
            db.add(cat_electronics)
            db.commit()
            db.refresh(cat_electronics)

        cat_fashion = db.query(Category).filter(Category.slug == "fashion").first()
        if not cat_fashion:
            cat_fashion = Category(
                name="Fashion",
                slug="fashion",
                description="Clothing, footwear, and accessories",
            )
            db.add(cat_fashion)
            db.commit()
            db.refresh(cat_fashion)

        # Sample products with distinct names for FTS & Fuzzy search testing
        sample_products = [
            ("Apple iPhone 15 Pro", "apple-iphone-15-pro", "Flagship smartphone with A17 Pro chip and titanium design", 999.99, 50, cat_electronics.id),
            ("Samsung Galaxy S24 Ultra", "samsung-galaxy-s24-ultra", "AI-powered flagship Android smartphone with 200MP camera", 1199.99, 40, cat_electronics.id),
            ("Apple MacBook Air M3", "apple-macbook-air-m3", "13-inch lightweight laptop with Apple silicon M3 chip", 1099.99, 30, cat_electronics.id),
            ("Dell XPS 15 Laptop", "dell-xps-15-laptop", "High performance OLED gaming and creator laptop", 1499.99, 25, cat_electronics.id),
            ("Sony WH-1000XM5 Headphones", "sony-wh-1000xm5-headphones", "Industry-leading wireless noise canceling headphones", 399.99, 80, cat_electronics.id),
            ("Logitech MX Master 3S Mouse", "logitech-mx-master-3s-mouse", "Ergonomic wireless mouse with quiet clicks and 8K DPI sensor", 99.99, 120, cat_electronics.id),
            ("Keychron K2 Mechanical Keyboard", "keychron-k2-mechanical-keyboard", "Wireless 75% layout mechanical keyboard with Gateron switches", 89.99, 60, cat_electronics.id),
            ("Men Casual Cotton Shirt", "men-casual-cotton-shirt", "Comfortable slim fit breathable button-down shirt", 34.99, 150, cat_fashion.id),
        ]

        print("3. Seeding sample catalog items...")
        for name, slug, desc, price, stock, cat_id in sample_products:
            prod = db.query(Product).filter(Product.slug == slug).first()
            if not prod:
                db.add(
                    Product(
                        name=name,
                        slug=slug,
                        description=desc,
                        price=price,
                        stock=stock,
                        category_id=cat_id,
                        is_active=True,
                    )
                )
        db.commit()

        # Seed sample User and Order for PDF testing
        user = db.query(User).filter(User.username == "testcustomer").first()
        if not user:
            user = User(
                username="testcustomer",
                email="customer@example.com",
                hashed_password="fakehashedpassword",
                full_name="Narasimha Test User",
                role=UserRole.CUSTOMER,
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        order = db.query(Order).first()
        if not order:
            order = Order(
                user_id=user.id,
                total_amount=1099.98,
                status=OrderStatus.CONFIRMED,
                shipping_address="H.No 12-34, Main Road, Guntur, AP, 522001",
            )
            db.add(order)
            db.commit()
            db.refresh(order)

        print("   Database successfully seeded!")

    finally:
        db.close()


if __name__ == "__main__":
    setup_indexes_and_seed()
