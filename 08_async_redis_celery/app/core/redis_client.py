import logging
from typing import Optional
import redis.asyncio as aioredis
import fakeredis.aioredis

from app.core.config import settings

logger = logging.getLogger("redis_client")

_redis_client: Optional[aioredis.Redis] = None
_is_fake: bool = False


async def init_redis() -> aioredis.Redis:
    """
    Initialize asynchronous Redis client.
    Attempts connection to configured REDIS_URL. If connection fails or Redis is
    not running, automatically falls back to an in-memory FakeRedis instance so that
    learning, development, and test suites run without external dependencies.
    """
    global _redis_client, _is_fake

    try:
        real_client = aioredis.from_url(
            settings.REDIS_URL,
            max_connections=settings.REDIS_MAX_CONNECTIONS,
            socket_timeout=settings.REDIS_TIMEOUT,
            socket_connect_timeout=settings.REDIS_TIMEOUT,
            decode_responses=True,
        )
        # Test connection
        await real_client.ping()
        _redis_client = real_client
        _is_fake = False
        logger.info(f"Connected to live Redis at {settings.REDIS_URL}")
        print(f"[Redis] Connected successfully to live Redis at {settings.REDIS_URL}")
    except Exception as exc:
        logger.warning(
            f"Unable to connect to live Redis ({exc}). Falling back to in-memory FakeRedis."
        )
        print(
            f"[Redis] Live Redis unavailable ({exc}). Using in-memory FakeRedis for full emulation."
        )
        _redis_client = fakeredis.aioredis.FakeRedis(decode_responses=True)
        _is_fake = True

    return _redis_client


async def close_redis() -> None:
    """Close the active Redis connection pool."""
    global _redis_client
    if _redis_client is not None:
        try:
            if hasattr(_redis_client, "aclose"):
                await _redis_client.aclose()
            else:
                await _redis_client.close()
            logger.info("Redis client connection closed.")

        except Exception as exc:
            logger.warning(f"Error closing Redis client: {exc}")
        finally:
            _redis_client = None


async def get_redis() -> aioredis.Redis:
    """
    FastAPI Dependency to retrieve active Redis client.
    Initializes automatically if not yet started.
    """
    global _redis_client
    if _redis_client is None:
        await init_redis()
    return _redis_client


def is_fake_redis() -> bool:
    """Check if the active client is using FakeRedis."""
    return _is_fake
