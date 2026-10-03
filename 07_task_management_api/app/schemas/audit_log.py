"""Audit log schemas for tracking task lifecycle transitions."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict
from app.schemas.user import UserSummary


class TaskAuditLogResponse(BaseModel):
    """Historical audit entry for a task transition or assignment."""
    id: int
    task_id: int
    changed_by_id: Optional[int] = None
    old_status: Optional[str] = None
    new_status: str
    notes: Optional[str] = None
    created_at: datetime
    changed_by: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)
