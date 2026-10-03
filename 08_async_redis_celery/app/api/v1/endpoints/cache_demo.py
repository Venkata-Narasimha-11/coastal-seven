import asyncio
import time
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

from app.api.deps import RedisDep
from app.services.cache_service import CacheService
from app.core.config import settings

router = APIRouter(prefix="/cache", tags=["Redis Caching"])

# Mock database repository
MOCK_PRODUCTS_DB = {
    101: {"id": 101, "name": "Mechanical Keyboard", "price": 129.99, "stock": 45},
    102: {"id": 102, "name": "Ultra-Wide Gaming Monitor", "price": 499.99, "stock": 12},
    103: {"id": 103, "name": "Ergonomic Mesh Chair", "price": 249.50, "stock": 20},
}


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, example="Mechanical Keyboard Pro RGB")
    price: Optional[float] = Field(None, example=149.99)
    stock: Optional[int] = Field(None, example=50)


@router.get("/products/{product_id}")
async def get_product_cache_aside(
    product_id: int,
    redis: RedisDep,
    ttl: int = settings.CACHE_DEFAULT_TTL_SECONDS
) -> Dict[str, Any]:
    """
    Demonstrates Cache-Aside (Lazy Loading) Pattern:
    1. Look up 'product:{id}' in Redis.
    2. HIT: Return cached JSON directly in < 5ms.
    3. MISS: Simulate slow database query (200ms), write to Redis with TTL, return fresh data.
    """
    start_time = time.perf_counter()
    cache_key = f"product:{product_id}"

    # Define fetcher to invoke only on cache miss
    async def fetch_from_db():
        await asyncio.sleep(0.20)  # Simulate expensive database disk seek / query
        if product_id not in MOCK_PRODUCTS_DB:
            return None
        return MOCK_PRODUCTS_DB[product_id]

    # Attempt cache-aside retrieval
    data, is_hit = await CacheService.get_or_set(
        redis=redis,
        key=cache_key,
        ttl_seconds=ttl,
        fetcher=fetch_from_db
    )

    if data is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Product with ID {product_id} not found."
        )

    elapsed_ms = round((time.perf_counter() - start_time) * 1000, 2)

    # Inquire remaining TTL from Redis
    ttl_remaining = await redis.ttl(cache_key)

    return {
        "cache_hit": is_hit,
        "source": "Redis Cache" if is_hit else "Simulated Database (200ms delay)",
        "response_time_ms": elapsed_ms,
        "cache_key": cache_key,
        "ttl_remaining_seconds": ttl_remaining,
        "data": data,
    }


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    payload: ProductUpdateSchema,
    redis: RedisDep
) -> Dict[str, Any]:
    """
    Demonstrates Cache Invalidation on Update:
    When updating an entity, we must evict/invalidate stale Redis keys
    to guarantee read consistency on the next fetch.
    """
    if product_id not in MOCK_PRODUCTS_DB:
        raise HTTPException(status_code=404, detail="Product not found")

    # Update persistent database
    product = MOCK_PRODUCTS_DB[product_id]
    if payload.name is not None:
        product["name"] = payload.name
    if payload.price is not None:
        product["price"] = payload.price
    if payload.stock is not None:
        product["stock"] = payload.stock

    # Invalidate cache key
    cache_key = f"product:{product_id}"
    deleted_keys = await CacheService.invalidate(redis, cache_key)

    return {
        "message": f"Product {product_id} updated successfully.",
        "cache_invalidated": deleted_keys > 0,
        "cache_key_purged": cache_key,
        "updated_data": product,
    }


@router.delete("/products/{product_id}")
async def delete_product(product_id: int, redis: RedisDep) -> Dict[str, Any]:
    """
    Demonstrates Cache Invalidation on Delete.
    """
    if product_id not in MOCK_PRODUCTS_DB:
        raise HTTPException(status_code=404, detail="Product not found")

    del MOCK_PRODUCTS_DB[product_id]
    cache_key = f"product:{product_id}"
    deleted_keys = await CacheService.invalidate(redis, cache_key)

    return {
        "message": f"Product {product_id} deleted successfully.",
        "cache_invalidated": deleted_keys > 0,
        "cache_key_purged": cache_key,
    }


@router.post("/purge-all")
async def purge_all_product_caches(redis: RedisDep) -> Dict[str, Any]:
    """
    Invalidates all product cache keys using pattern matching ('product:*').
    """
    deleted = await CacheService.invalidate_pattern(redis, "product:*")
    return {
        "message": "Product cache namespace purged.",
        "keys_cleared": deleted,
    }
