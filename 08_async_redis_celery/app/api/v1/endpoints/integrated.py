import asyncio
import time
from typing import Dict, Any
from fastapi import APIRouter, Depends, BackgroundTasks, Request

from app.api.deps import RedisDep, RateLimitDependency
from app.services.cache_service import CacheService
from app.services.rate_limiter import RateLimitResult
from app.services.external_api import ExternalApiService
from app.tasks.fastapi_bg import record_audit_log
from app.tasks.celery_tasks import generate_pdf_report_task

router = APIRouter(prefix="/integrated", tags=["Final Integration"])

# Sliding-Window Rate Limiter for Dashboard: 10 requests per 30 seconds
dashboard_rate_limiter = RateLimitDependency(max_requests=10, window_seconds=30, endpoint_tag="dashboard")


@router.get("/dashboard/{user_id}")
async def get_integrated_dashboard(
    user_id: str,
    request: Request,
    bg_tasks: BackgroundTasks,
    redis: RedisDep,
    rate_limit: RateLimitResult = Depends(dashboard_rate_limiter),
) -> Dict[str, Any]:
    """
    FINAL INTEGRATION ENDPOINT:
    Harmonizes all Day 8 core technologies into a unified production pipeline:
      1. Rate Limiting: Redis ZSET Sliding-Window verification (10 req/30s).
      2. Cache-Aside: Reads 'dashboard:{user_id}' from Redis (TTL 45s).
      3. Async Concurrency: On cache miss, executes 3 external API calls in parallel using asyncio.gather().
      4. FastAPI BackgroundTasks: Immediately queues in-process user access audit logging.
      5. Celery Background Job: Dispatches heavy analytics synchronization task to external Celery worker.
    """
    total_start = time.perf_counter()
    cache_key = f"dashboard:{user_id}"

    async def fetch_fresh_dashboard_data():
        """Executed ONLY on cache miss."""
        # Simulated user profile
        user_profile = {
            "user_id": user_id,
            "name": f"User {user_id.upper()}",
            "preferred_city": "San Francisco",
            "portfolio_ticker": "NVDA",
        }

        # CONCURRENT ASYNC CALLS VIA asyncio.gather()
        fetch_start = time.perf_counter()
        weather, rates, stock = await asyncio.gather(
            ExternalApiService.fetch_weather(user_profile["preferred_city"], simulated_delay=0.20),
            ExternalApiService.fetch_currency_rates("USD", simulated_delay=0.20),
            ExternalApiService.fetch_stock_quote(user_profile["portfolio_ticker"], simulated_delay=0.20),
        )
        fetch_elapsed = round(time.perf_counter() - fetch_start, 4)

        return {
            "profile": user_profile,
            "widgets": {
                "weather": weather,
                "currency_market": rates,
                "portfolio": stock,
            },
            "fetch_metrics": {
                "strategy": "asyncio.gather() concurrent I/O",
                "concurrent_duration_seconds": fetch_elapsed,
                "estimated_sequential_duration_seconds": round(0.20 * 3, 4),
                "speedup_factor": f"{round((0.20 * 3) / max(0.001, fetch_elapsed), 1)}x",
            }
        }

    # 1 & 2: Redis Cache-Aside lookup
    dashboard_data, is_cache_hit = await CacheService.get_or_set(
        redis=redis,
        key=cache_key,
        ttl_seconds=45,
        fetcher=fetch_fresh_dashboard_data
    )

    # 3: FastAPI In-Process BackgroundTasks
    client_ip = request.client.host if request.client else "127.0.0.1"
    bg_tasks.add_task(
        record_audit_log,
        action="VIEW_INTEGRATED_DASHBOARD",
        resource=f"user:{user_id}",
        client_ip=client_ip
    )

    # 4: Celery Out-of-Process Background Task
    celery_job = generate_pdf_report_task.delay(
        report_name=f"Dashboard_Snapshot_{user_id}",
        total_records=100
    )

    total_elapsed_ms = round((time.perf_counter() - total_start) * 1000, 2)
    ttl_remaining = await redis.ttl(cache_key)

    return {
        "status": "SUCCESS",
        "performance_and_architecture": {
            "total_response_time_ms": total_elapsed_ms,
            "cache": {
                "pattern": "Cache-Aside (Lazy Loading)",
                "hit": is_cache_hit,
                "key": cache_key,
                "ttl_remaining_seconds": ttl_remaining,
            },
            "rate_limiting": {
                "algorithm": "Redis Sorted Sets (ZSET) Sliding-Window",
                "remaining_quota": rate_limit.remaining,
                "limit": rate_limit.limit,
            },
            "background_processing": {
                "fastapi_background_tasks": "In-process audit log scheduled",
                "celery_distributed_task": {
                    "task_id": celery_job.id,
                    "state": "QUEUED",
                    "poll_url": f"/api/v1/tasks/celery/{celery_job.id}/status",
                }
            }
        },
        "data": dashboard_data,
    }


@router.post("/dashboard/{user_id}/refresh")
async def force_dashboard_refresh(user_id: str, redis: RedisDep) -> Dict[str, Any]:
    """
    Force cache invalidation for a user's dashboard.
    Ensures subsequent requests bypass cached data and re-invoke the concurrent async gather pipeline.
    """
    cache_key = f"dashboard:{user_id}"
    deleted = await CacheService.invalidate(redis, cache_key)
    return {
        "status": "REFRESHED",
        "cache_key": cache_key,
        "invalidated": deleted > 0,
        "message": f"Cache cleared for user {user_id}. Next dashboard fetch will reload live data.",
    }
