"""
Tutorial 2: Redis Caching Patterns & Sliding-Window Rate Limiting
================================================================
Covers:
  1. Cache-Aside Pattern (Lazy Loading) Workflow
  2. Time-To-Live (TTL) and Expiration Mechanics
  3. Cache Invalidation upon Data Mutation
  4. Sliding-Window Rate Limiting using Redis Sorted Sets (ZSET)

Run directly with:
  python tutorials/02_redis_caching_patterns.py
"""

import asyncio
import time
import json
import fakeredis.aioredis
from typing import Dict, Any


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# Mock persistent database with artificial disk latency
DB_STORAGE = {
    101: {"id": 101, "name": "Mechanical Keyboard", "price": 129.99, "stock": 45}
}


async def mock_slow_db_query(item_id: int) -> Dict[str, Any]:
    print("      [Database Query] Simulating slow DB read (250ms latency)...")
    await asyncio.sleep(0.25)
    return DB_STORAGE.get(item_id)


# ==============================================================================
# 1. Cache-Aside Workflow & TTL
# ==============================================================================
async def demo_cache_aside_and_ttl(redis):
    print_header("1. CACHE-ASIDE PATTERN & TIME-TO-LIVE (TTL)")
    key = "product:101"
    await redis.delete(key)

    # First access: Cache MISS
    print("--- [Step 1: First Request (Cache MISS)] ---")
    start = time.perf_counter()
    cached_val = await redis.get(key)
    if cached_val is None:
        print("   -> Redis Cache MISS! Querying persistent database...")
        data = await mock_slow_db_query(101)
        # Store in Redis with 3-second TTL
        await redis.set(key, json.dumps(data), ex=3)
        print("   -> Loaded into Redis cache with TTL=3 seconds.")
    else:
        data = json.loads(cached_val)
    t1 = (time.perf_counter() - start) * 1000
    print(f"   First fetch response time: {t1:.2f} ms\n")

    # Second access: Cache HIT
    print("--- [Step 2: Second Request (Cache HIT)] ---")
    start = time.perf_counter()
    cached_val = await redis.get(key)
    if cached_val is not None:
        print("   -> Redis Cache HIT! Read directly from memory.")
        data = json.loads(cached_val)
    t2 = (time.perf_counter() - start) * 1000
    ttl_remaining = await redis.ttl(key)
    print(f"   Second fetch response time: {t2:.2f} ms (Remaining TTL: {ttl_remaining}s)")
    print(f"   Speedup from Redis caching: {t1 / max(0.1, t2):.1f}x faster!\n")

    # Third access: Waiting for TTL Expiration
    print("--- [Step 3: Waiting 3.5 seconds for TTL expiration...] ---")
    await asyncio.sleep(3.5)
    expired_val = await redis.get(key)
    print(f"   Redis query after TTL: {expired_val} (Key automatically evicted from RAM)")


# ==============================================================================
# 2. Cache Invalidation
# ==============================================================================
async def demo_cache_invalidation(redis):
    print_header("2. CACHE INVALIDATION ON DATA UPDATE")
    key = "product:101"
    
    # Repopulate cache
    await redis.set(key, json.dumps(DB_STORAGE[101]), ex=60)
    print("   Cached item loaded in Redis: price = $129.99")

    # Now update item in DB
    print("\n   [Mutation Event] Product price updated in Database to $149.99")
    DB_STORAGE[101]["price"] = 149.99

    # Cache Invalidation: Stale cache eviction
    deleted = await redis.delete(key)
    print(f"   [Cache Invalidation] Stale key '{key}' deleted from Redis ({deleted} keys deleted)")

    # Subsequent read fetches fresh data
    fresh_val = await redis.get(key)
    print(f"   Next read detects cache miss (redis.get = {fresh_val}) -> refetches $149.99")


# ==============================================================================
# 3. Sliding-Window Rate Limiting using Redis Sorted Sets (ZSET)
# ==============================================================================
async def check_sliding_window(redis, user_ip: str, max_requests: int = 5, window_seconds: int = 4):
    now = time.time()
    window_start = now - window_seconds
    key = f"ratelimit:{user_ip}"

    # Atomic evaluation using Redis pipeline
    pipe = redis.pipeline()
    # 1. Purge requests older than sliding window
    pipe.zremrangebyscore(key, 0, window_start)
    # 2. Count current requests
    pipe.zcard(key)
    # 3. Add expire safety
    pipe.expire(key, window_seconds + 1)
    results = await pipe.execute()
    current_count = results[1]

    if current_count >= max_requests:
        # Rate limit breached
        oldest = await redis.zrange(key, 0, 0, withscores=True)
        retry_after = round((oldest[0][1] + window_seconds) - now, 2)
        return False, current_count, retry_after

    # Under limit: Record current request timestamp
    await redis.zadd(key, {f"{now}-{time.perf_counter()}": now})
    return True, current_count + 1, 0.0


async def demo_sliding_window_rate_limiting(redis):
    print_header("3. SLIDING-WINDOW RATE LIMITING (REDIS SORTED SETS)")
    user = "192.168.1.50"
    await redis.delete(f"ratelimit:{user}")
    print(f"Configuration: Maximum 5 requests allowed per 4-second rolling window.")
    print("Sending 7 rapid requests to test rate limiting...\n")

    for req_num in range(1, 8):
        allowed, count, retry_after = await check_sliding_window(redis, user, max_requests=5, window_seconds=4)
        if allowed:
            print(f"   Request {req_num}: [200 OK] Allowed! (Current in-window count: {count}/5)")
        else:
            print(f"   Request {req_num}: [429 TOO MANY REQUESTS] BLOCKED! Retry after: {retry_after}s")
        await asyncio.sleep(0.05)

    print("\nWaiting 4.2 seconds for sliding window to shift forward...")
    await asyncio.sleep(4.2)

    allowed, count, retry_after = await check_sliding_window(redis, user, max_requests=5, window_seconds=4)
    print(f"   Request 8 (After Window Reset): [200 OK] Allowed! (In-window count: {count}/5)")


async def main():
    print("=" * 70)
    print("    WELCOME TO DAY 8: REDIS CACHING & RATE LIMITING TUTORIAL")
    print("=" * 70)
    redis = fakeredis.aioredis.FakeRedis(decode_responses=True)
    try:
        await demo_cache_aside_and_ttl(redis)
        await demo_cache_invalidation(redis)
        await demo_sliding_window_rate_limiting(redis)
    finally:
        await redis.aclose()

    print("\n" + "=" * 70)
    print("  [OK] Redis Caching & Rate Limiting Tutorial Complete!")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
