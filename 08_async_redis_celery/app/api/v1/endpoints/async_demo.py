import asyncio
import time
from typing import Dict, Any
from fastapi import APIRouter, Query

from app.services.external_api import ExternalApiService

router = APIRouter(prefix="/async", tags=["Async Programming"])


@router.get("/concepts")
async def async_concepts() -> Dict[str, Any]:
    """
    Overview of Python Async Architecture:
    - Event Loop: Single-threaded multiplexer using OS I/O primitives (epoll/kqueue/IOCP).
    - Coroutines: Functions defined with 'async def' yielding control via 'await'.
    - async def vs def:
      * 'async def': Runs on the main event loop thread without thread context switching overhead.
      * 'def': In FastAPI, standard 'def' endpoints run in an external threadpool (Starlette threadpool)
        to prevent blocking the event loop. CPU-bound or blocking I/O in 'async def' freezes the loop!
    - asyncio.gather(): Schedules multiple coroutines concurrently, awaiting collective completion.
    """
    return {
        "event_loop": "Cooperative multitasking scheduler switching between tasks during I/O wait",
        "async_def_vs_def": {
            "async_def": "Non-blocking cooperative coroutine running directly on the event loop",
            "standard_def": "Handed off to Starlette threadpool; safe for blocking calls but incurs thread overhead",
            "rule_of_thumb": "Use 'async def' with non-blocking async drivers; use 'def' if calling blocking libraries"
        },
        "concurrency_primitive": "asyncio.gather(*aws, return_exceptions=False) runs coroutines concurrently"
    }


@router.get("/sequential")
async def run_sequential(
    city: str = Query("London", description="City for weather lookup"),
    currency: str = Query("USD", description="Base currency"),
    stock: str = Query("GOOGL", description="Stock ticker"),
) -> Dict[str, Any]:
    """
    Demonstrates SEQUENTIAL awaiting of 3 I/O calls.
    Notice how each service waits for the previous one to complete.
    Total Time ≈ sum(service_latencies).
    """
    return await ExternalApiService.run_sequential_demo(city, currency, stock)


@router.get("/concurrent")
async def run_concurrent(
    city: str = Query("London", description="City for weather lookup"),
    currency: str = Query("USD", description="Base currency"),
    stock: str = Query("GOOGL", description="Stock ticker"),
) -> Dict[str, Any]:
    """
    Demonstrates CONCURRENT awaiting of 3 I/O calls using asyncio.gather().
    All 3 services are initiated at the same instant on the event loop.
    Total Time ≈ max(service_latencies), achieving significant speedup!
    """
    return await ExternalApiService.run_concurrent_demo(city, currency, stock)


@router.get("/gather-error-handling")
async def gather_with_error_handling(simulate_error: bool = Query(True)) -> Dict[str, Any]:
    """
    Demonstrates asyncio.gather(..., return_exceptions=True).
    Without return_exceptions=True, a single failure aborts the entire gather immediately.
    With return_exceptions=True, individual exceptions are captured and returned as objects,
    allowing partial successes to be preserved.
    """
    async def task_success(n: int):
        await asyncio.sleep(0.1)
        return f"Task {n} completed successfully"

    async def task_failing():
        await asyncio.sleep(0.1)
        if simulate_error:
            raise ValueError("External third-party provider returned 503 Service Unavailable")
        return "Task succeeded"

    # Run gather with return_exceptions=True
    results = await asyncio.gather(
        task_success(1),
        task_failing(),
        task_success(2),
        return_exceptions=True
    )

    processed_results = []
    for idx, r in enumerate(results, 1):
        if isinstance(r, Exception):
            processed_results.append({"task": idx, "status": "ERROR", "error_type": type(r).__name__, "message": str(r)})
        else:
            processed_results.append({"task": idx, "status": "OK", "data": r})

    return {
        "strategy": "asyncio.gather(..., return_exceptions=True)",
        "advantage": "Resilient fault tolerance — prevents single dependency failure from crashing the request",
        "results": processed_results
    }
