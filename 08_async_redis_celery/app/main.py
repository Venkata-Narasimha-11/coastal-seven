from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.redis_client import init_redis, close_redis, is_fake_redis
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    FastAPI Lifespan Context Manager:
    Initializes async resources (Redis client connection pool) on startup,
    and cleanly closes connections on shutdown.
    """
    # Startup
    redis_client = await init_redis()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="""
## Day 8: Async Programming, Redis Caching & Celery Background Processing

Production-grade FastAPI architecture demonstrating:
* **Async Programming**: Event loop internals, coroutine execution, and `asyncio.gather()` for parallel I/O.
* **Redis Caching**: Cache-Aside (Lazy Loading) pattern, TTL expiration, and cache invalidation.
* **Rate Limiting**: Sliding-Window algorithm using Redis Sorted Sets (ZSET) preventing burst exploits.
* **Celery Background Tasks**: Offloading heavy work to distributed workers, tracking task states, and exponential backoff retries.
* **BackgroundTasks vs Celery**: Side-by-side analysis, tradeoffs, and decision framework.
* **Final Integration**: Multi-tiered endpoint combining async concurrency, caching, rate limiting, and background workers.
    """,
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API v1 router
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/", tags=["Root"])
async def root():
    return {
        "title": settings.PROJECT_NAME,
        "docs_url": "/docs",
        "health_check": "/health",
        "api_v1_prefix": settings.API_V1_STR,
        "redis_emulation_mode": "FakeRedis (In-Memory)" if is_fake_redis() else "Live Redis Server",
    }


@app.get("/health", tags=["Root"])
async def health_check():
    return {
        "status": "healthy",
        "redis": "connected",
        "fake_redis_active": is_fake_redis(),
    }
