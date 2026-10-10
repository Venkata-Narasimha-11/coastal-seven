"""Populates beautiful, high-resolution product images in the PostgreSQL database."""

from app.database import SessionLocal
from app.models import Product
from app.services.redis_service import CacheService

IMAGE_MAP = {
    "iphone": "https://images.unsplash.com/photo-1695048133142-1a20484d2569?w=600&auto=format&fit=crop&q=80",
    "galaxy": "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=600&auto=format&fit=crop&q=80",
    "macbook": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=600&auto=format&fit=crop&q=80",
    "dell": "https://images.unsplash.com/photo-1593642632823-8f785ba67e45?w=600&auto=format&fit=crop&q=80",
    "laptop": "https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=600&auto=format&fit=crop&q=80",
    "headphone": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=600&auto=format&fit=crop&q=80",
    "mouse": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=600&auto=format&fit=crop&q=80",
    "keyboard": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=600&auto=format&fit=crop&q=80",
    "monitor": "https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=600&auto=format&fit=crop&q=80",
    "watch": "https://images.unsplash.com/photo-1546868871-7041f2a55e12?w=600&auto=format&fit=crop&q=80",
    "fitness": "https://images.unsplash.com/photo-1575311373937-040b8e1fd5b6?w=600&auto=format&fit=crop&q=80",
    "soundbar": "https://images.unsplash.com/photo-1545454675-3531b543be5d?w=600&auto=format&fit=crop&q=80",
    "shirt": "https://images.unsplash.com/photo-1596755094514-f87e34085b2c?w=600&auto=format&fit=crop&q=80",
    "powerbank": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=600&auto=format&fit=crop&q=80",
    "charger": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=600&auto=format&fit=crop&q=80",
}

DEFAULT_IMAGE = "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=600&auto=format&fit=crop&q=80"


def get_image_for_name(name: str) -> str:
    name_lower = name.lower()
    for keyword, url in IMAGE_MAP.items():
        if keyword in name_lower:
            return url
    return DEFAULT_IMAGE


def main():
    db = SessionLocal()
    try:
        products = db.query(Product).all()
        updated_count = 0
        for p in products:
            if not p.image_url:
                p.image_url = get_image_for_name(p.name)
                p.thumbnail_url = p.image_url
                updated_count += 1
                print(f"Updated product #{p.id} '{p.name}' -> {p.image_url[:60]}...")

        db.commit()
        print(f"\nSuccessfully populated images for {updated_count} products!")
        
        # Invalidate Redis and app caches
        CacheService.invalidate_product_caches()
        print("Invalidated product caches.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
