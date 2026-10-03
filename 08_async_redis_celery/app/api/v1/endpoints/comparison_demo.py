from typing import Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, BackgroundTasks, Request, status

from app.tasks.fastapi_bg import record_audit_log, sync_write_telemetry, FASTAPI_BG_AUDIT_LOGS
from app.tasks.celery_tasks import generate_pdf_report_task

router = APIRouter(prefix="/tasks/comparison", tags=["BackgroundTasks vs Celery"])


class ActionPayload(BaseModel):
    action: str = Field(..., example="USER_LOGIN")
    resource_id: str = Field(..., example="USR-9843")


@router.get("/matrix")
async def get_comparison_matrix() -> Dict[str, Any]:
    """
    Architectural & Operational Decision Matrix: FastAPI BackgroundTasks vs Celery.
    """
    return {
        "title": "FastAPI BackgroundTasks vs Celery Architecture Guide",
        "comparison_table": [
            {
                "criterion": "Execution Model",
                "fastapi_background_tasks": "In-Process (runs directly inside the ASGI worker event loop or threadpool)",
                "celery": "Out-of-Process (dedicated worker processes or remote worker clusters)"
            },
            {
                "criterion": "Infrastructure & Complexity",
                "fastapi_background_tasks": "Zero extra infrastructure (runs in existing FastAPI app process)",
                "celery": "Requires message broker (Redis/RabbitMQ) + Result Backend + Celery worker processes"
            },
            {
                "criterion": "Persistence & Crash Safety",
                "fastapi_background_tasks": "Volatile / In-Memory (tasks are LOST if server crashes or restarts)",
                "celery": "Persistent (tasks stored in broker queue; safe against web server restarts and failures)"
            },
            {
                "criterion": "Horizontal Scalability",
                "fastapi_background_tasks": "Bound to web server instance CPU/RAM. Heavy jobs freeze or slow down API",
                "celery": "Independently scalable. Worker nodes can scale to 100s of instances independently"
            },
            {
                "criterion": "Retries & Fault Tolerance",
                "fastapi_background_tasks": "No built-in retry mechanism. Must write custom error handling",
                "celery": "Enterprise-grade: exponential backoff, jitter, max_retries, dead-letter queues"
            },
            {
                "criterion": "Periodic Scheduling",
                "fastapi_background_tasks": "None out of the box (requires external cron or libraries like APScheduler)",
                "celery": "Built-in cron scheduling with Celery Beat"
            },
            {
                "criterion": "Monitoring & Observability",
                "fastapi_background_tasks": "Manual application logging",
                "celery": "Real-time Flower web dashboard, task events, inspect APIs, Prometheus exporters"
            },
        ],
        "decision_rule": {
            "use_fastapi_background_tasks_when": [
                "Writing simple audit logs or telemetry right after returning HTTP response",
                "Sending a single notification or lightweight email on low-traffic service",
                "Updating in-memory caches or non-critical state",
                "You want zero infrastructure overhead without Redis or worker processes"
            ],
            "use_celery_when": [
                "Task is CPU-heavy (image/video compression, PDF generation, data analytics)",
                "Task is mission-critical (payment settlement, orders, data backups) and must survive crashes",
                "Automatic retries with exponential backoff are required for transient network flakiness",
                "Scheduled periodic jobs (cron jobs via Celery Beat)",
                "Heavy batch operations requiring task routing and independent worker scaling"
            ]
        }
    }


@router.post("/fastapi-bg", status_code=status.HTTP_200_OK)
async def run_fastapi_background_task(
    payload: ActionPayload,
    request: Request,
    bg_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Demonstrates FastAPI native BackgroundTasks:
    Schedules an audit log task to run in-process AFTER sending the HTTP response.
    Notice the response returns immediately without waiting for the task to finish.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"

    # Add async background task
    bg_tasks.add_task(record_audit_log, payload.action, payload.resource_id, client_ip)
    
    # Add sync background task (Starlette dispatches to threadpool)
    bg_tasks.add_task(sync_write_telemetry, "audit_events_count", 1.0)

    return {
        "status": "ACCEPTED_IN_PROCESS",
        "technology": "FastAPI BackgroundTasks",
        "action": payload.action,
        "resource_id": payload.resource_id,
        "message": "Task scheduled in-process. Runs immediately after response dispatch.",
        "note": "Volatile: will not survive process termination."
    }


@router.post("/celery", status_code=status.HTTP_202_ACCEPTED)
async def run_celery_task(payload: ActionPayload) -> Dict[str, Any]:
    """
    Demonstrates Celery Distributed Task Queue:
    Dispatches a heavy operation out-of-process to the Redis message broker.
    Task is persistent, isolated from web server resources, and tracked by ID.
    """
    task = generate_pdf_report_task.delay(
        report_name=f"Report_{payload.resource_id}",
        total_records=250
    )

    return {
        "status": "QUEUED_OUT_OF_PROCESS",
        "technology": "Celery Distributed Queue",
        "task_id": task.id,
        "message": "Task queued in Redis message broker for dedicated Celery workers.",
        "poll_status_url": f"/api/v1/tasks/celery/{task.id}/status",
        "note": "Persistent: survives web server crash; monitored via Flower."
    }


@router.get("/fastapi-bg/logs")
async def view_fastapi_bg_logs() -> Dict[str, Any]:
    """View the recent in-process audit logs captured by FastAPI BackgroundTasks."""
    return {
        "total_in_process_logs": len(FASTAPI_BG_AUDIT_LOGS),
        "recent_entries": FASTAPI_BG_AUDIT_LOGS[-10:]
    }
