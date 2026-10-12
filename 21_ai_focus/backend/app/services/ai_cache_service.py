"""Redis AI Response Caching Service.

Provides deterministic SHA-256 cache key generation, TTL expiration policies,
cache hit/miss tracking, and prefix invalidation for all AI endpoints.
"""

import hashlib
import json
import logging
import time
from typing import Any, Dict, Optional, Tuple

from app.config import settings
from app.services.redis_service import get_redis

logger = logging.getLogger("ai_cache_service")


class AICacheService:
    """Manages Redis caching for expensive AI operations (descriptions, search, moderation, agent)."""

    PREFIX_DESCRIPTION = "ai:cache:desc"
    PREFIX_SEMANTIC = "ai:cache:semantic"
    PREFIX_MODERATION = "ai:cache:mod"
    PREFIX_AGENT = "ai:cache:agent"

    @classmethod
    def generate_key(cls, prefix: str, payload: Any) -> str:
        """Generates a deterministic 16-character SHA-256 hash key from any payload."""
        if isinstance(payload, str):
            raw_str = payload.strip().lower()
        else:
            raw_str = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(raw_str.encode("utf-8")).hexdigest()[:16]
        return f"{prefix}:{digest}"

    @classmethod
    def get(cls, key: str) -> Tuple[Optional[Any], bool]:
        """Retrieves cached AI response if present.

        Returns:
            (cached_data, is_hit): Tuple containing data and boolean hit indicator.
        """
        r = get_redis()
        try:
            cached_raw = r.get(key)
            if cached_raw:
                cls._increment_metric("hits")
                data = json.loads(cached_raw)
                logger.debug("Redis AI Cache HIT for key: %s", key)
                return data, True
        except Exception as exc:
            logger.warning("Error reading from Redis AI cache (%s): %s", key, exc)

        cls._increment_metric("misses")
        return None, False

    @classmethod
    def set(cls, key: str, data: Any, ttl_seconds: Optional[int] = None) -> bool:
        """Stores AI response in Redis with specified TTL (defaults to REDIS_AI_CACHE_TTL_SECONDS)."""
        r = get_redis()
        ttl = ttl_seconds if ttl_seconds is not None else settings.REDIS_AI_CACHE_TTL_SECONDS
        try:
            serialized = json.dumps(data, default=str)
            r.set(key, serialized, ex=ttl)
            logger.debug("Redis AI Cache SET key: %s (TTL: %ds)", key, ttl)
            return True
        except Exception as exc:
            logger.warning("Error writing to Redis AI cache (%s): %s", key, exc)
            return False

    @classmethod
    def invalidate_prefix(cls, prefix: str) -> int:
        """Deletes all cache keys starting with the given prefix."""
        r = get_redis()
        pattern = f"{prefix}:*"
        try:
            keys = r.keys(pattern)
            if keys:
                count = r.delete(*keys)
                logger.info("Invalidated %d keys matching pattern: %s", count, pattern)
                return count
        except Exception as exc:
            logger.warning("Error invalidating cache pattern (%s): %s", pattern, exc)
        return 0

    @classmethod
    def clear_all_ai_caches(cls) -> int:
        """Clears all AI cache keys across descriptions, semantic search, moderation, and agent."""
        total = 0
        for prefix in [cls.PREFIX_DESCRIPTION, cls.PREFIX_SEMANTIC, cls.PREFIX_MODERATION, cls.PREFIX_AGENT]:
            total += cls.invalidate_prefix(prefix)
        return total

    @classmethod
    def _increment_metric(cls, metric_name: str) -> None:
        """Increments hit or miss counter in Redis."""
        try:
            r = get_redis()
            r.incr(f"ai:metrics:{metric_name}")
        except Exception:
            pass

    @classmethod
    def get_metrics(cls) -> Dict[str, Any]:
        """Returns cache hits, misses, and estimated latency saved."""
        try:
            r = get_redis()
            hits = int(r.get("ai:metrics:hits") or 0)
            misses = int(r.get("ai:metrics:misses") or 0)
            total = hits + misses
            hit_ratio = round((hits / total * 100), 2) if total > 0 else 0.0
            # Assume average LLM call saved is ~1,200ms
            latency_saved_sec = round((hits * 1.2), 2)

            return {
                "total_requests": total,
                "cache_hits": hits,
                "cache_misses": misses,
                "hit_ratio_percent": hit_ratio,
                "estimated_latency_saved_seconds": latency_saved_sec,
                "estimated_cost_saved_usd": round(hits * 0.002, 4),
            }
        except Exception as exc:
            logger.warning("Error reading AI cache metrics: %s", exc)
            return {
                "total_requests": 0,
                "cache_hits": 0,
                "cache_misses": 0,
                "hit_ratio_percent": 0.0,
                "estimated_latency_saved_seconds": 0.0,
                "estimated_cost_saved_usd": 0.0,
            }
