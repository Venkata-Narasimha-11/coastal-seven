"""
Tutorial 1: Python Asynchronous Programming Deep Dive
======================================================
Covers:
  1. Event Loop Mechanics & Cooperative Multitasking
  2. Coroutines: 'async def' vs standard 'def'
  3. Why Blocking the Event Loop Freezes Everything
  4. Concurrent Execution with asyncio.gather() Benchmark
  5. Resilient Error Handling with return_exceptions=True
  6. Task Timeouts via asyncio.wait_for()

Run directly with:
  python tutorials/01_async_deep_dive.py
"""

import asyncio
import time
from typing import List, Any


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ==============================================================================
# 1. Coroutines & Event Loop Inspection
# ==============================================================================
async def demo_event_loop_internals():
    print_header("1. EVENT LOOP INTERNALS & COOPERATIVE MULTITASKING")
    loop = asyncio.get_running_loop()
    print(f"Active Event Loop Class: {loop.__class__.__name__}")
    print(f"Is Loop Running?:         {loop.is_running()}")
    print("Core Concept: The Event Loop is a single-threaded multiplexer.")
    print("When a coroutine hits 'await', it yields execution back to the loop,")
    print("allowing other coroutines to execute while waiting for I/O.")


# ==============================================================================
# 2. 'async def' vs 'def' (Blocking vs Non-Blocking)
# ==============================================================================
async def async_worker(task_id: int, delay: float):
    print(f"   [Worker {task_id}] Started (asyncio.sleep {delay}s) -> yields to event loop")
    await asyncio.sleep(delay)
    print(f"   [Worker {task_id}] Finished non-blocking I/O!")
    return f"Result {task_id}"


async def demo_cooperative_multitasking():
    print_header("2. COOPERATIVE MULTITASKING WITH 'async def'")
    start = time.perf_counter()
    # Schedule two workers concurrently
    t1 = asyncio.create_task(async_worker(1, 0.3))
    t2 = asyncio.create_task(async_worker(2, 0.3))
    await t1
    await t2
    elapsed = time.perf_counter() - start
    print(f"\n   Total Elapsed Time for 2 x 0.3s async workers: {elapsed:.3f}s")
    print("   -> Notice both workers ran concurrently inside the same OS thread!\n")


# ==============================================================================
# 3. Benchmark: Sequential vs asyncio.gather() Parallelism
# ==============================================================================
async def simulate_api_call(service_name: str, latency: float = 0.25):
    print(f"   -> [API Request] Fetching from {service_name} (latency {latency}s)...")
    await asyncio.sleep(latency)
    print(f"   <- [API Response] Received payload from {service_name}!")
    return {"service": service_name, "status": 200, "data": f"{service_name}_data"}


async def demo_sequential_vs_gather():
    print_header("3. BENCHMARK: SEQUENTIAL AWAITS vs asyncio.gather()")
    
    # Sequential
    print("--- [Mode A: Sequential Awaits] ---")
    start_seq = time.perf_counter()
    r1 = await simulate_api_call("PaymentGateway", 0.25)
    r2 = await simulate_api_call("FraudDetector", 0.25)
    r3 = await simulate_api_call("InventoryService", 0.25)
    seq_time = time.perf_counter() - start_seq
    print(f"Sequential Execution Time: {seq_time:.3f}s (Sum of individual latencies)\n")

    # Concurrent via asyncio.gather()
    print("--- [Mode B: Concurrent asyncio.gather()] ---")
    start_conc = time.perf_counter()
    results = await asyncio.gather(
        simulate_api_call("PaymentGateway", 0.25),
        simulate_api_call("FraudDetector", 0.25),
        simulate_api_call("InventoryService", 0.25),
    )
    conc_time = time.perf_counter() - start_conc
    print(f"Concurrent Execution Time: {conc_time:.3f}s (Max of individual latencies)")
    print(f"Speedup Factor:            {seq_time / conc_time:.2f}x faster!\n")


# ==============================================================================
# 4. Error Handling in asyncio.gather(): return_exceptions=True
# ==============================================================================
async def demo_gather_error_handling():
    print_header("4. FAULT-TOLERANT GATHER: return_exceptions=True")
    
    async def reliable_service():
        await asyncio.sleep(0.1)
        return "Reliable Service Data"

    async def flaky_service():
        await asyncio.sleep(0.1)
        raise ConnectionResetError("Third-party gateway dropped connection!")

    print("Running gather with return_exceptions=True...")
    responses: List[Any] = await asyncio.gather(
        reliable_service(),
        flaky_service(),
        reliable_service(),
        return_exceptions=True
    )

    for i, res in enumerate(responses, 1):
        if isinstance(res, Exception):
            print(f"   Task {i}: FAILED with Exception: {type(res).__name__} ('{res}')")
        else:
            print(f"   Task {i}: SUCCESS -> {res}")
            
    print("Key Takeaway: return_exceptions=True allows partial successes without aborting everything!")


# ==============================================================================
# 5. Timeouts with asyncio.wait_for()
# ==============================================================================
async def demo_timeouts():
    print_header("5. PROTECTING CALLS WITH asyncio.wait_for(timeout=...)")
    
    async def slow_upstream_service():
        await asyncio.sleep(2.0)
        return "Slow payload"

    try:
        print("Awaiting slow service with 0.3s timeout...")
        await asyncio.wait_for(slow_upstream_service(), timeout=0.3)
    except asyncio.TimeoutError:
        print("   CAUGHT TimeoutError: Call exceeded 0.3s limit! Returning fallback gracefully.")


async def main():
    print("=" * 70)
    print("    WELCOME TO DAY 8: ASYNC PROGRAMMING TUTORIAL")
    print("=" * 70)
    await demo_event_loop_internals()
    await demo_cooperative_multitasking()
    await demo_sequential_vs_gather()
    await demo_gather_error_handling()
    await demo_timeouts()
    print("\n" + "=" * 70)
    print("  [OK] Async Programming Tutorial Complete!")

    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
