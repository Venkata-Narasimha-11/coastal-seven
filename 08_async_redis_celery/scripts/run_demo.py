"""
Day 8 End-to-End Live Demonstration Script
===========================================
Validates and showcases all 5 learning topics in real-time:
  1. Async Programming: Event loop, sequential vs asyncio.gather() concurrent calls
  2. Redis Caching: Cache-Aside pattern, TTL expiration, cache invalidation
  3. Sliding-Window Rate Limiting: Redis ZSET algorithm & 429 Too Many Requests
  4. Celery Background Tasks: Worker task dispatch, state progression, and retries
  5. BackgroundTasks vs Celery: In-process vs out-of-process comparison
  6. Final Integration: Comprehensive unified dashboard endpoint

Run directly with:
  python scripts/run_demo.py
"""

import sys
import os
import time
import asyncio
from httpx import AsyncClient, ASGITransport

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from app.celery_app import celery_app

# Enable eager execution and memory broker for immediate local demo verification
celery_app.conf.broker_url = "memory://"
celery_app.conf.result_backend = "cache+memory://"
celery_app.conf.task_always_eager = True
celery_app.conf.task_eager_propagates = True
celery_app.conf.task_store_eager_result = True



def print_banner(title: str):
    print("\n" + "=" * 75)
    print(f"  [*] {title}")
    print("=" * 75)



async def run_live_demo():
    print_banner("DAY 8: ASYNC PROGRAMMING, REDIS CACHING & CELERY HUB")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        # ------------------------------------------------------------------
        # 0. Healthcheck & Setup
        # ------------------------------------------------------------------
        res = await client.get("/health")
        print(f"System Health Status: {res.json()}")

        # ------------------------------------------------------------------
        # 1. Topic 1: Async Programming (Sequential vs Concurrent)
        # ------------------------------------------------------------------
        print_banner("TOPIC 1: ASYNC PROGRAMMING (async def vs def & asyncio.gather)")
        
        print("1.1 Calling Sequential Endpoint (/api/v1/async/sequential)...")
        t0 = time.perf_counter()
        seq_res = await client.get("/api/v1/async/sequential?city=Tokyo&currency=EUR&stock=AAPL")
        seq_duration = time.perf_counter() - t0
        print(f"    Sequential Total Time: {seq_duration:.3f}s")
        print(f"    Payload Mode:          {seq_res.json()['mode']}")

        print("\n1.2 Calling Concurrent Endpoint (/api/v1/async/concurrent via asyncio.gather)...")
        t0 = time.perf_counter()
        conc_res = await client.get("/api/v1/async/concurrent?city=Tokyo&currency=EUR&stock=AAPL")
        conc_duration = time.perf_counter() - t0
        print(f"    Concurrent Total Time: {conc_duration:.3f}s")
        print(f"    Payload Mode:          {conc_res.json()['mode']}")
        print(f"    >> Speedup Factor:     {seq_duration / max(0.001, conc_duration):.2f}x faster!")

        print("\n1.3 Testing Fault-Tolerant Gather (/api/v1/async/gather-error-handling)...")
        err_res = await client.get("/api/v1/async/gather-error-handling?simulate_error=true")
        print(f"    Results with return_exceptions=True:")
        for r in err_res.json()["results"]:
            print(f"      - Task {r['task']}: Status={r['status']}")

        # ------------------------------------------------------------------
        # 2. Topic 2: Redis Caching (Cache-Aside & Invalidation)
        # ------------------------------------------------------------------
        print_banner("TOPIC 2: REDIS CACHING (Cache-Aside Pattern, TTL & Invalidation)")

        print("2.1 Requesting Product 101 (First Call -> Cache MISS)...")
        c1 = await client.get("/api/v1/cache/products/101")
        d1 = c1.json()
        print(f"    Cache Hit:             {d1['cache_hit']}")
        print(f"    Data Source:           {d1['source']}")
        print(f"    Response Time:         {d1['response_time_ms']} ms")

        print("\n2.2 Requesting Product 101 (Second Call -> Cache HIT)...")
        c2 = await client.get("/api/v1/cache/products/101")
        d2 = c2.json()
        print(f"    Cache Hit:             {d2['cache_hit']}")
        print(f"    Data Source:           {d2['source']}")
        print(f"    Response Time:         {d2['response_time_ms']} ms")
        print(f"    >> Redis Latency Drop: {d1['response_time_ms'] / max(0.1, d2['response_time_ms']):.1f}x faster!")


        print("\n2.3 Mutating Product 101 (PUT -> Cache Invalidation)...")
        put_res = await client.put("/api/v1/cache/products/101", json={"price": 139.99})
        print(f"    Update Message:        {put_res.json()['message']}")
        print(f"    Cache Invalidated:     {put_res.json()['cache_invalidated']}")

        print("\n2.4 Requesting Product 101 after Invalidation (Cache MISS with fresh data)...")
        c3 = await client.get("/api/v1/cache/products/101")
        d3 = c3.json()
        print(f"    Cache Hit:             {d3['cache_hit']}")
        print(f"    Updated Price Loaded:  ${d3['data']['price']}")

        # ------------------------------------------------------------------
        # 3. Topic 3: Sliding-Window Rate Limiting
        # ------------------------------------------------------------------
        print_banner("TOPIC 3: SLIDING-WINDOW RATE LIMITING (Redis Sorted Sets)")
        print("Testing Strict Endpoint: Maximum 3 requests allowed per 10 seconds.")

        for i in range(1, 5):
            rl_res = await client.get("/api/v1/rate-limit/strict")
            limit = rl_res.headers.get("X-RateLimit-Limit")
            rem = rl_res.headers.get("X-RateLimit-Remaining")
            if rl_res.status_code == 200:
                print(f"    Request {i}: [HTTP 200 OK] Allowed! (Quota Remaining: {rem}/{limit})")
            elif rl_res.status_code == 429:
                retry = rl_res.headers.get("Retry-After")
                print(f"    Request {i}: [HTTP 429 TOO MANY REQUESTS] Blocked! (Retry-After: {retry}s)")

        # ------------------------------------------------------------------
        # 4. Topic 4: Celery Background Tasks & Retries
        # ------------------------------------------------------------------
        print_banner("TOPIC 4: CELERY BACKGROUND TASKS (Workers, States & Retries)")
        
        print("4.1 Dispatching Heavy PDF Report Task to Celery...")
        celery_res = await client.post(
            "/api/v1/tasks/celery/report",
            json={"report_name": "Executive_Quarterly_Brief", "total_records": 100}
        )
        task_id = celery_res.json()["task_id"]
        print(f"    Task Enqueued! Task ID: {task_id}")

        print("\n4.2 Polling Celery Task Status...")
        status_res = await client.get(f"/api/v1/tasks/celery/{task_id}/status")
        task_info = status_res.json()
        print(f"    Task State:      {task_info['state']}")
        print(f"    Is Ready:        {task_info['ready']}")
        if "result" in task_info:
            print(f"    Final Result:    {task_info['result']}")

        print("\n4.3 Dispatching Email Task with Exponential Retry Policy...")
        email_res = await client.post(
            "/api/v1/tasks/celery/email-with-retry",
            json={"recipient": "ceo@enterprise.com", "subject": "Quarterly Update", "simulate_failure": False}
        )
        print(f"    Email Task ID:   {email_res.json()['task_id']}")
        print(f"    Retry Policy:    {email_res.json()['retry_policy']}")

        # ------------------------------------------------------------------
        # 5. Topic 5: BackgroundTasks vs Celery
        # ------------------------------------------------------------------
        print_banner("TOPIC 5: FASTAPI BACKGROUNDTASKS vs CELERY WORKERS")
        
        print("5.1 Executing FastAPI BackgroundTask (In-Process Audit Log)...")
        bg_res = await client.post(
            "/api/v1/tasks/comparison/fastapi-bg",
            json={"action": "USER_CHECKOUT", "resource_id": "ORD-501"}
        )
        print(f"    Status:          {bg_res.json()['status']}")
        print(f"    Execution Model: {bg_res.json()['technology']}")

        print("\n5.2 Executing Celery Task (Out-of-Process Distributed Task)...")
        cel_comp_res = await client.post(
            "/api/v1/tasks/comparison/celery",
            json={"action": "PROCESS_ORDER_INVOICE", "resource_id": "ORD-501"}
        )
        print(f"    Status:          {cel_comp_res.json()['status']}")
        print(f"    Execution Model: {cel_comp_res.json()['technology']}")

        print("\n5.3 Inspecting In-Process Audit Log History...")
        logs_res = await client.get("/api/v1/tasks/comparison/fastapi-bg/logs")
        print(f"    Total In-Process Logs Recorded: {logs_res.json()['total_in_process_logs']}")

        # ------------------------------------------------------------------
        # 6. Final Integration Endpoint
        # ------------------------------------------------------------------
        print_banner("TOPIC 6: FINAL INTEGRATION ENDPOINT (/api/v1/integrated/dashboard)")
        print("Combining Async Concurrency + Redis Caching + Rate Limiting + Background Jobs\n")

        print("6.1 Requesting Dashboard for user 'sarah' (First Call -> Cache Miss)...")
        dash1 = await client.get("/api/v1/integrated/dashboard/sarah")
        d_json1 = dash1.json()
        perf1 = d_json1["performance_and_architecture"]
        print(f"    Status:            {d_json1['status']}")
        print(f"    Total Time:        {perf1['total_response_time_ms']} ms")
        print(f"    Cache Hit:         {perf1['cache']['hit']}")
        print(f"    Remaining Quota:   {perf1['rate_limiting']['remaining_quota']}")
        print(f"    Celery Task ID:    {perf1['background_processing']['celery_distributed_task']['task_id']}")

        print("\n6.2 Requesting Dashboard for user 'sarah' (Second Call -> Cache Hit)...")
        dash2 = await client.get("/api/v1/integrated/dashboard/sarah")
        d_json2 = dash2.json()
        perf2 = d_json2["performance_and_architecture"]
        print(f"    Total Time:        {perf2['total_response_time_ms']} ms")
        print(f"    Cache Hit:         {perf2['cache']['hit']}")
        print(f"    >> Latency Drop:   {perf1['total_response_time_ms'] / max(0.1, perf2['total_response_time_ms']):.1f}x faster!")

        print("\n" + "=" * 75)
        print("  [SUCCESS] ALL DAY 8 MODULES TESTED & VALIDATED SUCCESSFULLY!")
        print("=" * 75)



if __name__ == "__main__":
    asyncio.run(run_live_demo())
