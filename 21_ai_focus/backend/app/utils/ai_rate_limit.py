"""Per-User and Per-IP Rate Limiting for AI Endpoints.

Implements token bucket / sliding window rate limiting in Redis with tiered
limits:
- Authenticated Admin: 60 req/min
- Authenticated Customer: 20 req/min
- Anonymous Visitor: 5 req/min
"""

import logging
import time
from typing import Optional, Tuple
from fastapi import Request, HTTPException, Response, Depends
from jose import jwt, JWTError

from app.config import settings
from app.services.redis_service import get_redis
from app.utils.rate_limit import get_safe_client_ip

logger = logging.getLogger("ai_rate_limit")


class AIRateLimiter:
    """FastAPI Dependency for enforcing per-user rate limits on AI endpoints."""

    def __init__(self, custom_limit: Optional[int] = None):
        self.custom_limit = custom_limit

    def _resolve_identity(self, request: Request) -> Tuple[str, str, int]:
        """Resolves identity key, identity type, and allowed limit per minute.

        Returns:
            (identifier_key, role, limit_per_minute)
        """
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                user_id = payload.get("sub")
                role = payload.get("role", "customer")
                if user_id:
                    if role == "admin":
                        limit = self.custom_limit or int(settings.AI_RATE_LIMIT_ADMIN.split("/")[0])
                    else:
                        limit = self.custom_limit or int(settings.AI_RATE_LIMIT_USER.split("/")[0])
                    return f"ai:ratelimit:user:{user_id}", role, limit
            except JWTError:
                pass  # Fall back to IP-based rate limiting if token is invalid or expired

        # Anonymous visitor
        client_ip = get_safe_client_ip(request)
        limit = self.custom_limit or int(settings.AI_RATE_LIMIT_ANONYMOUS.split("/")[0])
        return f"ai:ratelimit:ip:{client_ip}", "anonymous", limit

    def __call__(self, request: Request, response: Response):
        """Enforces rate limit in Redis and attaches standard rate limit headers."""
        key, role, limit = self._resolve_identity(request)
        r = get_redis()
        current_window = int(time.time() // 60)
        window_key = f"{key}:{current_window}"

        try:
            # Atomic increment and expire
            current_count = r.incr(window_key)
            if current_count == 1:
                r.expire(window_key, 65)  # 60s window + 5s buffer

            remaining = max(0, limit - current_count)
            reset_seconds = 60 - int(time.time() % 60)

            # Set response headers
            response.headers["X-RateLimit-Limit"] = str(limit)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(reset_seconds)
            response.headers["X-RateLimit-Identity"] = role

            if current_count > limit:
                logger.warning(
                    "AI Rate limit exceeded for %s (%s). Count: %d, Limit: %d",
                    key, role, current_count, limit
                )
                response.headers["Retry-After"] = str(reset_seconds)
                raise HTTPException(
                    status_code=429,
                    detail={
                        "error": "Rate limit exceeded for AI endpoints",
                        "identity_type": role,
                        "limit_per_minute": limit,
                        "current_usage": current_count,
                        "retry_after_seconds": reset_seconds,
                        "message": (
                            f"You have exceeded your AI quota ({limit} requests/minute). "
                            f"Please retry in {reset_seconds} seconds."
                        )
                    },
                    headers={
                        "Retry-After": str(reset_seconds),
                        "X-RateLimit-Limit": str(limit),
                        "X-RateLimit-Remaining": "0",
                        "X-RateLimit-Reset": str(reset_seconds),
                    }
                )

        except HTTPException:
            raise
        except Exception as exc:
            # Graceful degradation if Redis has an issue: log error and allow request
            logger.error("Rate limiter Redis failure (%s): %s. Bypassing check.", key, exc)

        return True


# Global reusable dependency instances
ai_rate_limiter = AIRateLimiter()
ai_rate_limiter_strict = AIRateLimiter(custom_limit=5)
