from typing import Dict, Any
from fastapi import APIRouter, Depends

from app.api.deps import RateLimitDependency
from app.services.rate_limiter import RateLimitResult

router = APIRouter(prefix="/rate-limit", tags=["Rate Limiting"])

# Dependency instances
strict_rate_limiter = RateLimitDependency(max_requests=3, window_seconds=10, endpoint_tag="strict")
standard_rate_limiter = RateLimitDependency(max_requests=5, window_seconds=10, endpoint_tag="standard")


@router.get("/strict")
async def strict_endpoint(
    rate_limit: RateLimitResult = Depends(strict_rate_limiter)
) -> Dict[str, Any]:
    """
    Protected by a Strict Sliding-Window Rate Limit:
    - Maximum 3 requests allowed per 10 seconds.
    - If you send a 4th request within 10 seconds, HTTP 429 Too Many Requests is returned.
    """
    return {
        "status": "SUCCESS",
        "message": "Access granted to strict endpoint.",
        "rate_limiting": {
            "algorithm": "Redis Sorted Sets (ZSET) Sliding-Window",
            "limit": rate_limit.limit,
            "remaining": rate_limit.remaining,
            "window_seconds": 10,
        },
    }


@router.get("/standard")
async def standard_endpoint(
    rate_limit: RateLimitResult = Depends(standard_rate_limiter)
) -> Dict[str, Any]:
    """
    Protected by Standard Sliding-Window Rate Limit:
    - Maximum 5 requests allowed per 10 seconds.
    """
    return {
        "status": "SUCCESS",
        "message": "Access granted to standard endpoint.",
        "rate_limiting": {
            "algorithm": "Redis Sorted Sets (ZSET) Sliding-Window",
            "limit": rate_limit.limit,
            "remaining": rate_limit.remaining,
            "window_seconds": 10,
        },
    }
