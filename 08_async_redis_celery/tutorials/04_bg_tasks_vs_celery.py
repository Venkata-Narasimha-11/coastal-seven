"""
Tutorial 4: FastAPI BackgroundTasks vs Celery Architectural Comparison
======================================================================
Covers:
  1. Deep Architectural Differences (In-Process vs Out-of-Process)
  2. Failure Scenarios & Crash Resilience (Volatile vs Persistent)
  3. Resource Impact: What happens when tasks are CPU heavy?
  4. Comprehensive Decision Flowchart and Workload Selection Guide

Run directly with:
  python tutorials/04_bg_tasks_vs_celery.py
"""


def print_header(title: str):
    print("\n" + "=" * 75)
    print(f"  {title}")
    print("=" * 75)


def explain_execution_models():
    print_header("1. IN-PROCESS (FASTAPI) vs OUT-OF-PROCESS (CELERY)")
    print("""
    A) FASTAPI BackgroundTasks (In-Process):
    ----------------------------------------
       HTTP Request  ---> [ ASGI Worker Process (Uvicorn) ]
                                |
                                +---> Runs Endpoint Logic
                                +---> Sends HTTP Response <--- (Client unblocked)
                                +---> Executes BackgroundTask inside the SAME process!
       
       Characteristics:
         * Zero infrastructure (no Redis, no RabbitMQ, no extra worker process).
         * Runs either on the async event loop or Starlette threadpool.
         * Shares CPU & RAM with incoming HTTP requests.

    B) CELERY (Out-of-Process & Distributed):
    -----------------------------------------
       HTTP Request  ---> [ Uvicorn Web Server ]
                                | (Sends task payload JSON)
                                v
                        [ Redis Message Broker ]
                                | (Pulls task from queue)
                                v
                         [ Celery Worker Pool ] ---> [ Result Backend ]
                         (Isolated OS Processes on independent machines)
       
       Characteristics:
         * Completely decoupled: Web server never does the heavy lifting.
         * Worker nodes can be autoscaled based on queue depth.
         * Survives crashes, web deployments, and reboots.
    """)


def explain_crash_resilience():
    print_header("2. FAILURE SCENARIOS & CRASH RESILIENCE")
    print("""
    Scenario 1: Web Server Crashes / Redeploys while 50 tasks are pending
    -------------------------------------------------------------------
    * FastAPI BackgroundTasks: 
        [FAIL] 100% OF TASKS ARE LOST.
        They live in Python process memory (RAM). When the process terminates,
        all scheduled background tasks vanish without trace.
    * Celery:
        [PASS] 0% LOSS.
        Task messages remain safely stored inside the persistent Redis/RabbitMQ
        broker queue. As soon as workers boot up, tasks resume execution!

    Scenario 2: Worker encounters transient network timeout
    -------------------------------------------------------------------
    * FastAPI BackgroundTasks:
        [FAIL] Unhandled exceptions fail silently or crash the task.
        No built-in retry mechanism or exponential backoff.
    * Celery:
        [PASS] Configured retries automatically reschedule task with backoff & jitter.
        Dead-letter queues collect permanently failed tasks for inspection.
    """)


def explain_cpu_impact():
    print_header("3. WHAT HAPPENS WITH CPU-BOUND TASKS?")
    print("""
    If you put a CPU-heavy task (e.g. 10-second image resizing or ML model inference)
    into FastAPI BackgroundTasks:
      * Python's Global Interpreter Lock (GIL) is saturated.
      * Even with threads, CPU-bound work starves the async event loop!
      * Incoming HTTP requests freeze, latencies spike from 10ms to 10,000ms!

    Rule: NEVER run CPU-heavy operations in FastAPI BackgroundTasks.
    Always offload CPU-heavy or long-running (> 500ms) operations to Celery.
    """)


def show_decision_framework():
    print_header("4. DECISION MATRIX: WHEN TO CHOOSE EACH")
    rows = [
        ("Criterion", "FastAPI BackgroundTasks", "Celery Distributed Queue"),
        ("Infrastructure", "None required", "Redis / RabbitMQ + Workers"),
        ("Operational Cost", "Zero extra servers", "Requires broker & worker nodes"),
        ("Persistence", "Volatile (Lost on crash)", "Persistent (Survives crash)"),
        ("Scaling", "Bound to single web node", "Scale horizontally to 100+ nodes"),
        ("Retries", "Manual implementation", "Native exponential backoff & jitter"),
        ("Cron Schedules", "Not supported", "Native with Celery Beat"),
        ("Monitoring", "Application logs only", "Flower Real-Time UI Dashboard"),
        ("Ideal Tasks", "Audit logs, emails (low vol)", "PDF/video render, batch sync, ML"),
    ]
    
    col_w = [18, 26, 32]
    header = f"| {rows[0][0]:<{col_w[0]}} | {rows[0][1]:<{col_w[1]}} | {rows[0][2]:<{col_w[2]}} |"
    divider = f"|{'-' * (col_w[0] + 2)}|{'-' * (col_w[1] + 2)}|{'-' * (col_w[2] + 2)}|"
    print(header)
    print(divider)
    for r in rows[1:]:
        print(f"| {r[0]:<{col_w[0]}} | {r[1]:<{col_w[1]}} | {r[2]:<{col_w[2]}} |")

    print("""
    Summary Cheat Sheet:
      --> Choose FastAPI BackgroundTasks if:
         - Task takes < 200ms
         - Zero tragedy if the task fails or drops on restart (e.g. logging)
         - You want zero operational complexity

      --> Choose Celery if:
         - Task takes > 500ms or is CPU-heavy
         - Task MUST be guaranteed to finish (billing, order processing)
         - You need automated retries, rate limits, or cron scheduling
    """)


def main():
    print("=" * 75)
    print("    WELCOME TO DAY 8: BACKGROUNDTASKS VS CELERY ARCHITECTURE GUIDE")
    print("=" * 75)
    explain_execution_models()
    explain_crash_resilience()
    explain_cpu_impact()
    show_decision_framework()
    print("=" * 75)
    print("  [OK] BackgroundTasks vs Celery Tutorial Complete!")
    print("=" * 75)


if __name__ == "__main__":
    main()
