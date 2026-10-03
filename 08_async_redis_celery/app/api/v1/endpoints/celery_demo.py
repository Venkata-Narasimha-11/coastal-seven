from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks.celery_tasks import generate_pdf_report_task, send_email_with_retry_task

router = APIRouter(prefix="/tasks/celery", tags=["Celery Background Tasks"])


class ReportRequest(BaseModel):
    report_name: str = Field(..., example="Q3_Financial_Summary")
    total_records: int = Field(500, example=500)


class EmailRetryRequest(BaseModel):
    recipient: str = Field(..., example="user@example.com")
    subject: str = Field("System Notification", example="Important Account Alert")
    simulate_failure: bool = Field(True, description="Simulate transient failures to test Celery automatic retries")


@router.post("/report", status_code=status.HTTP_202_ACCEPTED)
async def dispatch_pdf_report(payload: ReportRequest) -> Dict[str, Any]:
    """
    Offload a heavy report generation job to external Celery worker processes.
    Immediately returns HTTP 202 Accepted with a task_id for non-blocking polling.
    """
    task = generate_pdf_report_task.delay(
        report_name=payload.report_name,
        total_records=payload.total_records
    )

    return {
        "status": "QUEUED",
        "task_id": task.id,
        "report_name": payload.report_name,
        "message": "Task successfully enqueued to Celery broker. Check status via polling endpoint.",
        "poll_status_url": f"/api/v1/tasks/celery/{task.id}/status",
    }


@router.get("/{task_id}/status")
async def get_task_status(task_id: str) -> Dict[str, Any]:
    """
    Inspect the live lifecycle state of a Celery background task:
    Possible states: PENDING, STARTED, PROGRESS, RETRY, SUCCESS, FAILURE, REVOKED.
    """
    result = AsyncResult(task_id, app=celery_app)

    response: Dict[str, Any] = {
        "task_id": task_id,
        "state": result.state,
        "ready": result.ready(),
        "successful": result.successful() if result.ready() else False,
    }

    if result.state == "PROGRESS":
        response["progress"] = result.info
    elif result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.info)
    elif result.state == "RETRY":
        response["retry_info"] = str(result.info)
    else:
        response["info"] = "Task is currently awaiting an idle Celery worker or in transit."

    return response


@router.post("/email-with-retry", status_code=status.HTTP_202_ACCEPTED)
async def dispatch_email_with_retries(payload: EmailRetryRequest) -> Dict[str, Any]:
    """
    Dispatches task with Celery automatic exponential backoff retries.
    If simulate_failure=True, Celery catches ConnectionError, schedules retries
    with backoff (2s, 4s, 8s) + jitter, and succeeds on the 3rd attempt.
    """
    task = send_email_with_retry_task.delay(
        recipient=payload.recipient,
        subject=payload.subject,
        simulate_failure=payload.simulate_failure,
    )

    return {
        "status": "QUEUED",
        "task_id": task.id,
        "recipient": payload.recipient,
        "retry_policy": {
            "max_retries": 3,
            "retry_backoff": 2,
            "retry_jitter": True,
            "handled_exceptions": ["ConnectionError", "TimeoutError"],
        },
        "poll_status_url": f"/api/v1/tasks/celery/{task.id}/status",
    }


@router.post("/{task_id}/revoke")
async def revoke_task(task_id: str, terminate: bool = False) -> Dict[str, Any]:
    """
    Revoke/Cancel a Celery task.
    If terminate=True, sends SIGTERM/SIGKILL to the worker executing the task.
    """
    try:
        celery_app.control.revoke(task_id, terminate=terminate)
    except Exception:
        # Gracefully handle when running in local eager/testing mode without active cluster broadcast
        pass

    return {
        "task_id": task_id,
        "action": "REVOKED",
        "terminated": terminate,
        "message": f"Task {task_id} cancellation request broadcasted to workers."
    }

