import json
import functools
import logging
from typing import Any, Callable, Optional, Tuple
import redis.asyncio as aioredis

logger = logging.getLogger("cache_service")


class CacheService:
    """
    Production-grade implementation of Cache-Aside (Lazy Loading) pattern with Redis.
    Flow:
      1. Check Redis for cache key.
      2. If HIT: parse JSON and return immediately.
      3. If MISS: execute provider callback (e.g. database query, slow calculation).
      4. Save computed result to Redis with specified Time-To-Live (TTL).
      5. Return fresh data.
    """

    @staticmethod
    async def get(redis: aioredis.Redis, key: str) -> Optional[Any]:
        """Fetch raw or deserialized data from Redis cache."""
        try:
            val = await redis.get(key)
            if val is not None:
                return json.loads(val)
        except Exception as exc:
            logger.warning(f"Cache get error for key '{key}': {exc}")
        return None

    @staticmethod
    async def set(
        redis: aioredis.Redis,
        key: str,
        value: Any,
        ttl_seconds: int = 60
    ) -> bool:
        """Serialize data to JSON and store in Redis with TTL expiration."""
        try:
            serialized = json.dumps(value, default=str)
            await redis.set(key, serialized, ex=ttl_seconds)
            return True
        except Exception as exc:
            logger.warning(f"Cache set error for key '{key}': {exc}")
            return False

    @staticmethod
    async def get_or_set(
        redis: aioredis.Redis,
        key: str,
        ttl_seconds: int,
        fetcher: Callable[[], Any]
    ) -> Tuple[Any, bool]:
        """
        Execute Cache-Aside workflow.
        Returns: (data, is_cache_hit: bool)
        """
        cached_val = await CacheService.get(redis, key)
        if cached_val is not None:
            logger.debug(f"[CACHE HIT] Key: {key}")
            return cached_val, True

        logger.debug(f"[CACHE MISS] Key: {key}. Executing fetcher...")
        fresh_data = await fetcher() if callable(fetcher) else fetcher
        await CacheService.set(redis, key, fresh_data, ttl_seconds=ttl_seconds)
        return fresh_data, False

    @staticmethod
    async def invalidate(redis: aioredis.Redis, *keys: str) -> int:
        """
        Explicitly invalidate (delete) specific cache keys upon update or delete mutations.
        """
        if not keys:
            return 0
        try:
            deleted_count = await redis.delete(*keys)
            logger.info(f"Invalidated {deleted_count} cache keys: {keys}")
            return deleted_count
        except Exception as exc:
            logger.warning(f"Error invalidating cache keys {keys}: {exc}")
            return 0

    @staticmethod
    async def invalidate_pattern(redis: aioredis.Redis, pattern: str) -> int:
        """
        Invalidate all keys matching a wildcard pattern (e.g. 'products:*').
        """
        try:
            keys = await redis.keys(pattern)
            if keys:
                return await redis.delete(*keys)
            return 0
        except Exception as exc:
            logger.warning(f"Error invalidating pattern '{pattern}': {exc}")
            return 0


def cached(ttl_seconds: int = 60, prefix: str = "cache"):
    """
    Decorator for async functions implementing Cache-Aside automatically based on function arguments.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, redis: aioredis.Redis, **kwargs):
            # Build deterministic cache key from prefix, function name, and arguments
            key_args = [str(a) for a in args]
            key_kwargs = [f"{k}={v}" for k, v in sorted(kwargs.items())]
            cache_key = f"{prefix}:{func.__name__}:{':'.join(key_args + key_kwargs)}"
            
            cached_result = await CacheService.get(redis, cache_key)
            if cached_result is not None:
                return cached_result
            
            result = await func(*args, redis=redis, **kwargs)
            await CacheService.set(redis, cache_key, result, ttl_seconds=ttl_seconds)
            return result
        return wrapper
    return decorator
