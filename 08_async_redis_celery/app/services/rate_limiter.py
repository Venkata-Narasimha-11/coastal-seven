import time
import uuid
import logging
from dataclasses import dataclass
from typing import Optional
import redis.asyncio as aioredis

logger = logging.getLogger("rate_limiter")


@dataclass
class RateLimitResult:
    allowed: bool
    limit: int
    remaining: int
    retry_after: float
    reset_in_seconds: float


class SlidingWindowRateLimiter:
    """
    Sliding-Window Rate Limiter powered by Redis Sorted Sets (ZSET).
    
    Why Sliding Window over Fixed Window?
      - Fixed Window allows burst exploitation (e.g. 5 requests at 00:00:59 and 5 at 00:01:00 = 10 requests within 2 seconds).
      - Sliding Window inspects exact timestamps continuously, ensuring the threshold is never exceeded over ANY rolling window of T seconds.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 10):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    async def check_rate_limit(
        self,
        redis: aioredis.Redis,
        identifier: str,
        endpoint_key: str = "default",
        custom_max_requests: Optional[int] = None,
        custom_window_seconds: Optional[int] = None,
    ) -> RateLimitResult:
        """
        Evaluate sliding window for given client identifier.
        """
        max_req = custom_max_requests or self.max_requests
        window_sec = custom_window_seconds or self.window_seconds

        now = time.time()
        window_start = now - window_sec
        key = f"ratelimit:{identifier}:{endpoint_key}"

        # Atomic transaction with Redis Pipeline
        pipe = redis.pipeline()
        # 1. Remove all timestamps older than the sliding window start
        pipe.zremrangebyscore(key, 0, window_start)
        # 2. Count requests currently remaining inside the sliding window
        pipe.zcard(key)
        # 3. Ensure key TTL does not leak memory in Redis
        pipe.expire(key, window_sec + 2)
        
        results = await pipe.execute()
        current_count = results[1]

        if current_count >= max_req:
            # Over quota: inspect the oldest request to calculate exact retry_after
            oldest_entries = await redis.zrange(key, 0, 0, withscores=True)
            if oldest_entries:
                oldest_ts = oldest_entries[0][1]
                retry_after = max(0.1, round((oldest_ts + window_sec) - now, 2))
            else:
                retry_after = float(window_sec)
            
            logger.warning(
                f"[Rate Limit Exceeded] Identifier '{identifier}' hit {current_count}/{max_req} requests."
            )
            return RateLimitResult(
                allowed=False,
                limit=max_req,
                remaining=0,
                retry_after=retry_after,
                reset_in_seconds=retry_after,
            )

        # Under quota: record current request timestamp in the Sorted Set
        req_token = f"{now}-{uuid.uuid4().hex[:6]}"
        add_pipe = redis.pipeline()
        add_pipe.zadd(key, {req_token: now})
        add_pipe.expire(key, window_sec + 2)
        await add_pipe.execute()

        remaining = max(0, max_req - (current_count + 1))
        return RateLimitResult(
            allowed=True,
            limit=max_req,
            remaining=remaining,
            retry_after=0.0,
            reset_in_seconds=float(window_sec),
        )
