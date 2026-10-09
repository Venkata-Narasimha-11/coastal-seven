import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from decimal import Decimal
from app.database import SessionLocal, Base, engine
from app.models import Category, Product
from app.services.redis_service import CacheService


def seed_more():
    db = SessionLocal()
    try:
        # 1. New Categories
        categories_data = [
            {"name": "Laptops & Computers", "slug": "laptops-computers", "description": "High performance ultrabooks and PCs"},
            {"name": "Gaming & VR", "slug": "gaming-vr", "description": "Consoles, controllers, and VR headsets"},
            {"name": "Cameras & Drones", "slug": "cameras-drones", "description": "Professional 4K cameras and aerial drones"},
            {"name": "Smart Home", "slug": "smart-home", "description": "Smart speakers, lights, and thermostats"},
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

        # Existing categories mapping
        for c in db.query(Category).all():
            cat_map[c.slug] = c

        # 2. Rich Catalog of Additional Products with Verified Unsplash HD Images
        more_products = [
            {
                "name": "Apple MacBook Pro 16\" M3 Max",
                "slug": "apple-macbook-pro-16-m3-max",
                "description": "36GB unified memory, 1TB SSD, Liquid Retina XDR display with ProMotion.",
                "price": Decimal("3499.00"),
                "stock": 10,
                "category_id": cat_map["laptops-computers"].id,
                "image_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Dell XPS 15 InfinityEdge OLED Laptop",
                "slug": "dell-xps-15-infinityedge-oled",
                "description": "Intel Core i9 13th Gen, 32GB RAM, NVIDIA RTX 4070, 3.5K OLED touch display.",
                "price": Decimal("2299.99"),
                "stock": 14,
                "category_id": cat_map["laptops-computers"].id,
                "image_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Sony PlayStation 5 Slim Console",
                "slug": "sony-playstation-5-slim-console",
                "description": "Experience lightning-fast loading with an ultra-high speed SSD and 4K 120Hz support.",
                "price": Decimal("499.99"),
                "stock": 18,
                "category_id": cat_map["gaming-vr"].id,
                "image_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1606813907291-d86efa9b94db?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Meta Quest 3 512GB VR Headset",
                "slug": "meta-quest-3-512gb-vr-headset",
                "description": "Breakthrough mixed reality headset with 4K+ Infinite Display and 3D spatial audio.",
                "price": Decimal("649.99"),
                "stock": 15,
                "category_id": cat_map["gaming-vr"].id,
                "image_url": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1622979135225-d2ba269bc1df?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Xbox Wireless Controller - Carbon Black",
                "slug": "xbox-wireless-controller-carbon-black",
                "description": "Sculpted surfaces, hybrid D-pad, textured grip, and Bluetooth compatibility.",
                "price": Decimal("59.99"),
                "stock": 45,
                "category_id": cat_map["gaming-vr"].id,
                "image_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "DJI Mini 4 Pro 4K Drone",
                "slug": "dji-mini-4-pro-4k-drone",
                "description": "Under 249g folding drone with omnidirectional active obstacle sensing and 4K/60fps HDR.",
                "price": Decimal("759.00"),
                "stock": 8,
                "category_id": cat_map["cameras-drones"].id,
                "image_url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1507582020474-9a35b7d455d9?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Fujifilm X-T5 Mirrorless Camera Body",
                "slug": "fujifilm-xt5-mirrorless-camera",
                "description": "40.2MP X-Trans CMOS 5 HR sensor, 6.2K movie recording, and 5-axis IBIS.",
                "price": Decimal("1699.99"),
                "stock": 6,
                "category_id": cat_map["cameras-drones"].id,
                "image_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Amazon Echo Studio Smart Hi-Fi Speaker",
                "slug": "amazon-echo-studio-smart-speaker",
                "description": "Immersive 3D audio with Dolby Atmos, Alexa built-in, and spatial room adaptation.",
                "price": Decimal("199.99"),
                "stock": 30,
                "category_id": cat_map["smart-home"].id,
                "image_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1543512214-318c7553f230?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Bose QuietComfort Ultra Wireless Earbuds",
                "slug": "bose-quietcomfort-ultra-earbuds",
                "description": "World-class noise cancellation, CustomTune technology, and immersive spatial audio.",
                "price": Decimal("299.00"),
                "stock": 22,
                "category_id": cat_map["audio"].id if "audio" in cat_map else cat_map["smart-home"].id,
                "image_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=600&auto=format&fit=crop&q=80",
            },
            {
                "name": "Samsung Galaxy Watch 6 Classic",
                "slug": "samsung-galaxy-watch-6-classic",
                "description": "Rotating bezel, advanced sleep coaching, ECG monitoring, and sapphire crystal glass.",
                "price": Decimal("329.99"),
                "stock": 16,
                "category_id": cat_map["wearables"].id if "wearables" in cat_map else cat_map["smart-home"].id,
                "image_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80",
                "thumbnail_url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=600&auto=format&fit=crop&q=80",
            },
        ]

        count = 0
        for pdata in more_products:
            prod = db.query(Product).filter(Product.slug == pdata["slug"]).first()
            if not prod:
                prod = Product(**pdata, is_active=True)
                db.add(prod)
                count += 1

        db.commit()
        CacheService.invalidate_product_caches()
        print(f"Successfully added {count} new products with HD images!")

    except Exception as e:
        db.rollback()
        print("Error seeding more products:", e)
    finally:
        db.close()


if __name__ == "__main__":
    seed_more()
