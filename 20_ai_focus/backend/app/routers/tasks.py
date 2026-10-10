"""Background task tracking and execution router with strict Role-Based Access Control (RBAC)."""

import shutil
from pathlib import Path
from typing import Any, Dict
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session
from celery.result import AsyncResult

from app.config import settings
from app.database import get_db
from app.models import Order, User, UserRole
from app.utils.auth import get_current_admin, get_current_user
from app.utils.rate_limit import limiter
from app.services.celery_app import (
    celery_app,
    generate_pdf_invoice_task,
    bulk_import_products_csv_task,
)

router = APIRouter(prefix="/tasks", tags=["Background Tasks"])


# -------------------------------------------------------------
# 1. POLLING ENDPOINT: Task Status & Progress Check (Authenticated)
# -------------------------------------------------------------
@router.get("/{task_id}")
def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Returns the real-time lifecycle state and progress of any Celery task.
    Requires user to be authenticated.
    """
    task_result = AsyncResult(task_id, app=celery_app)

    if task_result.state == "PENDING":
        return {
            "task_id": task_id,
            "state": "PENDING",
            "progress": 0,
            "message": "Task is queued and waiting for worker...",
        }
    elif task_result.state == "PROGRESS":
        info = task_result.info or {}
        return {
            "task_id": task_id,
            "state": "PROGRESS",
            "progress": info.get("progress", 0),
            "message": info.get("message", "Processing task..."),
            "meta": info,
        }
    elif task_result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "state": "SUCCESS",
            "progress": 100,
            "message": "Task completed successfully!",
            "result": task_result.result,
        }
    elif task_result.state == "FAILURE":
        return {
            "task_id": task_id,
            "state": "FAILURE",
            "progress": 100,
            "message": "Task execution failed.",
            "error": str(task_result.info),
        }
    else:
        return {
            "task_id": task_id,
            "state": task_result.state,
            "progress": 0,
            "message": f"Task in {task_result.state} state",
        }


# -------------------------------------------------------------
# 2. TRIGGER ENDPOINT: PDF Invoice (Admin: Any order, User: Own order)
# -------------------------------------------------------------
@router.post("/orders/{order_id}/invoice", status_code=status.HTTP_202_ACCEPTED)
def trigger_order_invoice_generation(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Triggers background task to generate PDF invoice.
    Admin can generate for any order; Customer can only generate for their own order.
    """
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Order #{order_id} not found",
        )

    # RBAC check: Non-admin users can ONLY generate invoices for their own orders
    if current_user.role != UserRole.ADMIN and order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: you do not own this order to generate its invoice",
        )

    task = generate_pdf_invoice_task.delay(order_id)
    return {
        "task_id": task.id,
        "message": "PDF Invoice generation has started in the background",
        "order_id": order_id,
    }


# -------------------------------------------------------------
# 3. TRIGGER ENDPOINT: Upload CSV and Start Bulk Import (Admin ONLY)
# -------------------------------------------------------------
@router.post("/products/import-csv", status_code=status.HTTP_202_ACCEPTED)
@limiter.limit("3/minute")
def trigger_csv_product_import(
    request: Request,
    file: UploadFile = File(...),
    admin: User = Depends(get_current_admin),
) -> Dict[str, Any]:
    """
    Uploads a CSV file and triggers bulk product import background task.
    Strictly restricted to users with ADMIN role.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be a valid .csv file",
        )

    # Save uploaded file temporarily
    upload_dir = settings.UPLOAD_DIR / "imports"
    upload_dir.mkdir(parents=True, exist_ok=True)
    temp_file_path = upload_dir / f"uploaded_{file.filename}"

    with open(temp_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Dispatch Celery background task
    task = bulk_import_products_csv_task.delay(str(temp_file_path))

    return {
        "task_id": task.id,
        "message": "Bulk CSV import started in the background",
        "filename": file.filename,
    }