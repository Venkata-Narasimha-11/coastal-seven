"""
Tutorial 3: Celery Background Tasks, Workers, Retries & Monitoring
===================================================================
Covers:
  1. Celery Distributed Architecture (Producer -> Broker -> Worker -> Backend)
  2. Task Lifecycle States (PENDING, STARTED, PROGRESS, SUCCESS, RETRY, FAILURE)
  3. Automatic Retries with Exponential Backoff and Jitter
  4. Celery Beat Periodic Scheduling
  5. Flower Real-Time Monitoring Dashboard

Run directly with:
  python tutorials/03_celery_architecture.py
"""

import time
import random
from datetime import datetime


def print_header(title: str):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


# ==============================================================================
# 1. Celery Component Topology
# ==============================================================================
def explain_celery_topology():
    print_header("1. CELERY DISTRIBUTED TOPOLOGY")
    print("""
       [ FastAPI Web Server ]  (Task Producer)
                 |
                 | 1. task.delay(args) (Pushes message JSON)
                 v
       [ Redis Broker (Queue) ] (Task Message Buffer)
                 |
                 | 2. Worker pulls message from queue
                 v
       [ Celery Worker Pool ]  (Independent OS processes/nodes)
                 |
                 | 3. Writes result & status updates
                 v
       [ Redis Result Backend ] (Stores status, error, return payload)
                 ^
                 | 4. GET /tasks/{id}/status queries AsyncResult
       [ Client / Browser ]
    """)

    print("Why Celery?")
    print("  * Offloads heavy CPU/IO work so web endpoints respond in < 15ms.")
    print("  * Fault tolerant: if API crashes, task remains in broker queue.")
    print("  * Scale workers independently across dozens of machines.")


# ==============================================================================
# 2. Task Lifecycle States
# ==============================================================================
def demo_task_state_machine():
    print_header("2. TASK LIFECYCLE STATE MACHINE")
    states = [
        ("PENDING", "Task message sits in Redis broker awaiting an available worker."),
        ("STARTED", "Worker process picked up message and began execution (task_track_started=True)."),
        ("PROGRESS", "Worker published custom intermediate progress (e.g. 50% completed)."),
        ("RETRY",   "Task hit transient error; Celery scheduled delayed retry."),
        ("SUCCESS", "Task finished execution and result stored in Redis result backend."),
        ("FAILURE", "Task exceeded max retries or raised unhandled fatal exception."),
        ("REVOKED", "Task cancelled by administrator before or during execution."),
    ]
    for state, desc in states:
        print(f"   [{state:<8}] -> {desc}")


# ==============================================================================
# 3. Retry Simulation with Exponential Backoff & Jitter
# ==============================================================================
def simulate_retry_backoff(max_retries=3, base_backoff=2):
    print_header("3. RETRY STRATEGY: EXPONENTIAL BACKOFF + JITTER")
    print(f"Configuration: max_retries={max_retries}, base={base_backoff}s, retry_jitter=True\n")

    for retry in range(1, max_retries + 1):
        # Exponential formula: base * (2 ** (retry - 1))
        exponential_delay = base_backoff * (2 ** (retry - 1))
        # Jitter: adds random float between 0 and 1000ms to desynchronize concurrent retries
        jitter = round(random.uniform(0.1, 0.5), 2)
        total_delay = round(exponential_delay + jitter, 2)
        
        print(f"   Attempt {retry}/{max_retries} Failed: ConnectionTimeout")
        print(f"   -> Calculated Backoff: {exponential_delay}s + Jitter: {jitter}s = {total_delay}s sleep")
        print(f"   -> Scheduling retry #{retry} to execute after {total_delay}s...\n")

    print("Key Benefit of Jitter: Prevents the 'Thundering Herd' problem where thousands of")
    print("failed workers retry external databases at the exact same millisecond!")


# ==============================================================================
# 4. Celery Beat Periodic Scheduling
# ==============================================================================
def explain_celery_beat():
    print_header("4. CELERY BEAT PERIODIC SCHEDULING")
    print("""
    Celery Beat acts as a central distributed clock:
    It does NOT execute tasks itself. Instead, it inspects your beat_schedule
    and pushes task messages into the Redis broker at specified intervals or crontabs.

    Example Schedule:
      beat_schedule = {
          "heartbeat-every-minute": {
              "task": "app.tasks.celery_tasks.periodic_heartbeat_task",
              "schedule": 60.0,
          },
          "daily-sales-report-midnight": {
              "task": "app.tasks.celery_tasks.daily_sales_report",
              "schedule": crontab(hour=0, minute=0),
          }
      }

    Run Command:
      celery -A celery_beat.celery_app beat --loglevel=info
    """)


# ==============================================================================
# 5. Flower Real-Time Monitoring
# ==============================================================================
def explain_flower_monitoring():
    print_header("5. FLOWER REAL-TIME MONITORING")
    print("""
    Flower is the official web-based monitoring tool for Celery:
      * View live workers, memory consumption, active pools
      * Inspect queued, active, succeeded, and failed tasks in real-time
      * Revoke/terminate runaway tasks with 1 click
      * View runtime graphs, latency percentiles, and retry chains

    How to Launch:
      celery -A app.celery_app.celery_app flower --port=5555

    Then navigate in your browser to:
      http://localhost:5555
    """)


def main():
    print("=" * 70)
    print("    WELCOME TO DAY 8: CELERY ARCHITECTURE TUTORIAL")
    print("=" * 70)
    explain_celery_topology()
    demo_task_state_machine()
    simulate_retry_backoff()
    explain_celery_beat()
    explain_flower_monitoring()
    print("=" * 70)
    print("  [OK] Celery Architecture Tutorial Complete!")

    print("=" * 70)


if __name__ == "__main__":
    main()
