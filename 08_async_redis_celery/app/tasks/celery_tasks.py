import time
import logging
from datetime import datetime
from app.celery_app import celery_app

logger = logging.getLogger("celery_tasks")


@celery_app.task(bind=True, name="app.tasks.celery_tasks.generate_pdf_report_task")
def generate_pdf_report_task(self, report_name: str, total_records: int = 100):
    """
    Simulates a heavy, long-running batch job (e.g. PDF generation, analytics computation).
    Updates Celery custom task state during execution so clients can track progress.
    """
    logger.info(f"Starting PDF generation task: {report_name} for {total_records} records.")
    
    steps = 4
    delay_per_step = 0.02 if getattr(self.app.conf, "task_always_eager", False) else 0.5
    for i in range(1, steps + 1):
        time.sleep(delay_per_step)  # Simulate chunk processing
        percent = int((i / steps) * 100)

        self.update_state(
            state="PROGRESS",
            meta={
                "current_step": i,
                "total_steps": steps,
                "percent": percent,
                "message": f"Processing batch {i}/{steps}..."
            }
        )
        logger.info(f"Task {self.request.id} progress: {percent}%")

    result = {
        "status": "COMPLETED",
        "report_name": report_name,
        "records_processed": total_records,
        "file_url": f"/downloads/reports/{report_name}.pdf",
        "generated_at": datetime.utcnow().isoformat(),
    }
    return result


@celery_app.task(
    bind=True,
    name="app.tasks.celery_tasks.send_email_with_retry_task",
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=2,          # Exponential backoff base: 2s, 4s, 8s...
    retry_jitter=True,        # Add randomness to prevent thundering herd
    max_retries=3,
)
def send_email_with_retry_task(self, recipient: str, subject: str, simulate_failure: bool = False):
    """
    Demonstrates Celery automatic task retries with exponential backoff and jitter.
    If simulate_failure is True, it fails on first 2 attempts, then succeeds on 3rd retry.
    """
    logger.info(
        f"[Attempt {self.request.retries + 1}/{self.max_retries + 1}] Sending email to {recipient} with subject '{subject}'"
    )

    if simulate_failure and self.request.retries < 2:
        logger.warning(f"Simulating network transient failure on retry attempt {self.request.retries + 1}")
        raise ConnectionError(f"Transient SMTP gateway timeout on attempt {self.request.retries + 1}")

    return {
        "status": "DELIVERED",
        "recipient": recipient,
        "subject": subject,
        "attempts": self.request.retries + 1,
        "sent_at": datetime.utcnow().isoformat(),
    }


@celery_app.task(name="app.tasks.celery_tasks.periodic_heartbeat_task")
def periodic_heartbeat_task():
    """
    Celery Beat scheduled task running every 60 seconds to demonstrate periodic cron jobs.
    """
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"[Celery Beat] Periodic Heartbeat executed at {timestamp}")
    return {"heartbeat": "OK", "timestamp": timestamp}


@celery_app.task(name="app.tasks.celery_tasks.periodic_cleanup_cache_task")
def periodic_cleanup_cache_task():
    """
    Celery Beat scheduled task to simulate scheduled midnight cache/session purge.
    """
    timestamp = datetime.utcnow().isoformat()
    logger.info(f"[Celery Beat] Midnight cache maintenance executed at {timestamp}")
    return {"cleaned_keys": 42, "timestamp": timestamp}
