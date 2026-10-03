from typing import Annotated, Callable
from fastapi import Depends, HTTPException, Request, Response, status
import redis.asyncio as aioredis

from app.core.redis_client import get_redis
from app.services.rate_limiter import SlidingWindowRateLimiter, RateLimitResult
from app.core.config import settings

# Dependency alias for Redis Client
RedisDep = Annotated[aioredis.Redis, Depends(get_redis)]


class RateLimitDependency:
    """
    FastAPI dependency factory that enforces Sliding-Window Rate Limiting.
    Extracts client IP, checks Redis sorted set, adds X-RateLimit-* headers to Response,
    and returns 429 Too Many Requests when the limit is breached.
    """

    def __init__(self, max_requests: int = 5, window_seconds: int = 10, endpoint_tag: str = "api"):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.endpoint_tag = endpoint_tag
        self.limiter = SlidingWindowRateLimiter(max_requests, window_seconds)

    async def __call__(
        self,
        request: Request,
        response: Response,
        redis: RedisDep
    ) -> RateLimitResult:
        # Extract client IP or forward-header for identification
        client_ip = request.headers.get("x-forwarded-for") or (request.client.host if request.client else "127.0.0.1")
        
        result = await self.limiter.check_rate_limit(
            redis=redis,
            identifier=client_ip,
            endpoint_key=self.endpoint_tag,
            custom_max_requests=self.max_requests,
            custom_window_seconds=self.window_seconds,
        )

        # Standard Rate Limiting Headers (RFC 6585 & IETF draft)
        response.headers["X-RateLimit-Limit"] = str(result.limit)
        response.headers["X-RateLimit-Remaining"] = str(result.remaining)
        response.headers["X-RateLimit-Reset"] = str(int(result.reset_in_seconds))

        if not result.allowed:
            response.headers["Retry-After"] = str(int(result.retry_after))
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={
                    "error": "Too Many Requests",
                    "message": f"Rate limit exceeded. Maximum {result.limit} requests per {self.window_seconds} seconds.",
                    "retry_after_seconds": result.retry_after,
                },
                headers={"Retry-After": str(int(result.retry_after))},
            )

        return result
