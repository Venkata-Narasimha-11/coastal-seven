import asyncio
import logging
from datetime import datetime

logger = logging.getLogger("fastapi_bg")

# In-memory log buffer to demonstrate in-process execution
FASTAPI_BG_AUDIT_LOGS = []


async def record_audit_log(action: str, resource: str, client_ip: str) -> None:
    """
    Lightweight, in-process background task executed via FastAPI BackgroundTasks.
    Runs asynchronously inside the same event loop / threadpool right after the HTTP response is sent.
    """
    await asyncio.sleep(0.05)  # Simulate small non-blocking I/O
    log_entry = {
        "action": action,
        "resource": resource,
        "client_ip": client_ip,
        "executed_at": datetime.utcnow().isoformat(),
        "runner": "FastAPI_BackgroundTasks (In-Process)",
    }
    FASTAPI_BG_AUDIT_LOGS.append(log_entry)
    logger.info(f"[FastAPI BackgroundTasks] Audit log written: {log_entry}")


def sync_write_telemetry(metric_name: str, value: float) -> None:
    """
    Synchronous function executed inside FastAPI BackgroundTasks.
    Starlette runs synchronous background tasks in an external worker threadpool.
    """
    logger.info(f"[FastAPI BackgroundTasks Sync] Telemetry recorded: {metric_name}={value}")
