"""Redis service handling temporary shopping cart operations and API caching."""

import json
import logging
from decimal import Decimal
from typing import Any, Dict, List, Optional
import redis
from sqlalchemy.orm import Session
from app.config import settings
from app.models.product import Product

logger = logging.getLogger("redis_service")

# Initialize Redis client with automatic fallback to FakeRedis if server is offline
try:
    _real_client = redis.Redis.from_url(
        settings.REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=1.0,
        socket_timeout=1.0,
    )
    _real_client.ping()
    redis_client = _real_client
    logger.info("Connected to live Redis server at %s", settings.REDIS_URL)
except Exception:
    import fakeredis
    redis_client = fakeredis.FakeRedis(decode_responses=True)
    logger.warning("Live Redis server unreachable. Falling back to in-memory FakeRedis.")


def get_redis() -> redis.Redis:
    """Dependency / accessor for Redis client."""
    return redis_client


# ---------------------------------------------------------
# Cart Management Service (Stored in Redis Hashes)
# ---------------------------------------------------------

class CartService:
    """Manages high-speed shopping cart sessions stored in Redis Hashes.
    
    Structure:
    Key: `cart:{user_id}`
    Fields: `{product_id}` -> `quantity`
    """

    @staticmethod
    def _cart_key(user_id: int) -> str:
        return f"cart:{user_id}"

    @classmethod
    def add_to_cart(cls, user_id: int, product_id: int, quantity: int, db: Session) -> Dict[str, Any]:
        """Add product to user's Redis cart or increment quantity."""
        r = get_redis()
        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found or inactive")

        key = cls._cart_key(user_id)
        current_qty_str = r.hget(key, str(product_id))
        current_qty = int(current_qty_str) if current_qty_str else 0
        new_qty = current_qty + quantity

        if new_qty > product.stock:
            raise ValueError(
                f"Requested quantity ({new_qty}) exceeds available inventory ({product.stock})"
            )

        r.hset(key, str(product_id), str(new_qty))
        r.expire(key, settings.REDIS_CART_TTL_SECONDS)

        return cls.get_cart(user_id, db)

    @classmethod
    def update_quantity(cls, user_id: int, product_id: int, quantity: int, db: Session) -> Dict[str, Any]:
        """Update product quantity in cart. If quantity <= 0, remove item."""
        r = get_redis()
        key = cls._cart_key(user_id)
        if quantity <= 0:
            r.hdel(key, str(product_id))
            return cls.get_cart(user_id, db)

        product = db.query(Product).filter(Product.id == product_id, Product.is_active == True).first()
        if not product:
            raise ValueError(f"Product with ID {product_id} not found or inactive")

        if quantity > product.stock:
            raise ValueError(
                f"Requested quantity ({quantity}) exceeds available inventory ({product.stock})"
            )

        r.hset(key, str(product_id), str(quantity))
        r.expire(key, settings.REDIS_CART_TTL_SECONDS)

        return cls.get_cart(user_id, db)

    @classmethod
    def remove_item(cls, user_id: int, product_id: int) -> bool:
        """Remove a single product from the user's cart."""
        r = get_redis()
        key = cls._cart_key(user_id)
        deleted = r.hdel(key, str(product_id))
        return bool(deleted)

    @classmethod
    def get_cart(cls, user_id: int, db: Session) -> Dict[str, Any]:
        """Retrieve cart items, compute live subtotals, and check stock availability."""
        r = get_redis()
        key = cls._cart_key(user_id)
        raw_cart = r.hgetall(key)

        if not raw_cart:
            return {
                "items": [],
                "total_items": 0,
                "total_amount": Decimal("0.00"),
            }

        product_ids = [int(pid) for pid in raw_cart.keys()]
        products = db.query(Product).filter(Product.id.in_(product_ids)).all()
        product_map = {p.id: p for p in products}

        items: List[Dict[str, Any]] = []
        total_items = 0
        total_amount = Decimal("0.00")

        for pid_str, qty_str in raw_cart.items():
            pid = int(pid_str)
            qty = int(qty_str)
            product = product_map.get(pid)

            if not product or not product.is_active:
                # Cleanup orphaned items
                r.hdel(key, pid_str)
                continue

            subtotal = Decimal(str(product.price)) * qty
            total_items += qty
            total_amount += subtotal

            items.append({
                "product_id": product.id,
                "product_name": product.name,
                "unit_price": product.price,
                "quantity": qty,
                "subtotal": subtotal,
                "thumbnail_url": product.thumbnail_url or product.image_url,
                "available_stock": product.stock,
            })

        return {
            "items": items,
            "total_items": total_items,
            "total_amount": total_amount,
        }

    @classmethod
    def clear_cart(cls, user_id: int) -> bool:
        """Clear all items from user's shopping cart."""
        r = get_redis()
        key = cls._cart_key(user_id)
        r.delete(key)
        return True


# ---------------------------------------------------------
# Product Caching Service (Cache-Aside Pattern)
# ---------------------------------------------------------

class CacheService:
    """Manages Redis caching for read-heavy product catalog APIs."""

    @staticmethod
    def get(key: str) -> Optional[Any]:
        """Retrieve and parse JSON cached data."""
        try:
            r = get_redis()
            cached = r.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.error("Error reading cache for %s: %s", key, e)
        return None

    @staticmethod
    def set(key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Serialize data to JSON and store in Redis with TTL."""
        try:
            r = get_redis()
            ttl = ttl_seconds or settings.REDIS_CACHE_TTL_SECONDS
            serialized = json.dumps(data, default=str)
            r.set(key, serialized, ex=ttl)
            return True
        except Exception as e:
            logger.error("Error writing cache for %s: %s", key, e)
            return False

    @staticmethod
    def invalidate_pattern(pattern: str) -> int:
        """Delete all cache keys matching a pattern."""
        try:
            r = get_redis()
            keys = r.keys(pattern)
            if keys:
                return r.delete(*keys)
        except Exception as e:
            logger.error("Error invalidating cache pattern %s: %s", pattern, e)
        return 0

    @classmethod
    def invalidate_product_caches(cls, product_id: Optional[int] = None) -> None:
        """Invalidate product lists and specific product detail cache."""
        cls.invalidate_pattern("products:list:*")
        if product_id:
            r = get_redis()
            r.delete(f"product:detail:{product_id}")
