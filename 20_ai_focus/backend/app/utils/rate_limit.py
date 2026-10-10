"""Rate limiting configuration and safe client IP resolution utilities using SlowAPI."""

import logging
from fastapi import Request
from slowapi import Limiter
from app.config import settings

logger = logging.getLogger("rate_limit")


def get_safe_client_ip(request: Request) -> str:
    """Safely extracts client IP.

    Only trusts X-Forwarded-For if connecting peer is in TRUSTED_PROXIES.
    Otherwise, returns the connecting socket peer IP to prevent spoofing.
    """
    client_host = request.client.host if request.client else "127.0.0.1"

    if client_host in settings.TRUSTED_PROXIES:
        x_forwarded_for = request.headers.get("X-Forwarded-For")
        if x_forwarded_for:
            # First IP in X-Forwarded-For is the originating client IP
            origin_ip = x_forwarded_for.split(",")[0].strip()
            if origin_ip:
                return origin_ip

    return client_host


# Configure Rate Limit Storage:
# In production, shared Redis is strictly required. In dev/test, fallback to memory:// with a warning if Redis is down.
if settings.ENVIRONMENT == "production":
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=2.0)
        client.ping()
        client.close()
        _storage_uri = settings.REDIS_URL
    except Exception as exc:
        raise RuntimeError(
            f"FATAL: Production rate limiting requires accessible Redis at {settings.REDIS_URL}. Cannot start. Error: {exc}"
        )
else:
    try:
        import redis
        client = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1.0)
        client.ping()
        client.close()
        _storage_uri = settings.REDIS_URL
    except Exception:
        logger.warning(
            "Redis offline in %s mode. Rate limiting using in-memory storage (memory://).",
            settings.ENVIRONMENT,
        )
        _storage_uri = "memory://"

limiter = Limiter(
    key_func=get_safe_client_ip,
    default_limits=["100/minute"],
    storage_uri=_storage_uri,
)

__all__ = ["limiter", "get_safe_client_ip"]
