"""Task schemas for validation, serialization, workflow transitions, and filtering."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.core.workflow import TaskPriority, TaskStatus
from app.schemas.audit_log import TaskAuditLogResponse
from app.schemas.user import UserSummary


class TaskBase(BaseModel):
    """Base schema for task properties."""
    title: str = Field(min_length=2, max_length=180, description="Task title")
    description: Optional[str] = Field(default=None, max_length=5000, description="Task description")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Workflow status")
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, description="Priority level")
    due_date: Optional[datetime] = Field(default=None, description="Due date in ISO 8601")
    assignee_id: Optional[int] = Field(default=None, description="Assigned user ID")


class TaskCreate(BaseModel):
    """Payload to create a new task."""
    title: str = Field(min_length=2, max_length=180)
    description: Optional[str] = Field(default=None, max_length=5000)
    project_id: int = Field(description="Parent project ID")
    priority: Optional[TaskPriority] = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    """Payload for full task update (PUT)."""
    title: str = Field(min_length=2, max_length=180)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: TaskPriority
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskPatch(BaseModel):
    """Payload for partial task update (PATCH)."""
    title: Optional[str] = Field(default=None, min_length=2, max_length=180)
    description: Optional[str] = Field(default=None, max_length=5000)
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    """Payload to perform a workflow status transition."""
    status: TaskStatus = Field(description="Target workflow status")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Optional transition notes")


class TaskAssignRequest(BaseModel):
    """Payload to assign or reassign a task."""
    assignee_id: Optional[int] = Field(description="User ID to assign to, or null to unassign")
    notes: Optional[str] = Field(default=None, max_length=1000, description="Optional assignment notes")


class TaskResponse(BaseModel):
    """Standard task response model."""
    id: int
    title: str
    description: Optional[str] = None
    status: TaskStatus
    priority: TaskPriority
    due_date: Optional[datetime] = None
    project_id: int
    assignee_id: Optional[int] = None
    creator_id: int
    created_at: datetime
    updated_at: datetime
    assignee: Optional[UserSummary] = None
    creator: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class TaskDetailResponse(TaskResponse):
    """Detailed task model including available transitions and audit log trail."""
    allowed_transitions: List[str] = Field(
        default_factory=list,
        description="Valid status transitions permitted from current status",
    )
    audit_logs: List[TaskAuditLogResponse] = Field(
        default_factory=list,
        description="Historical timeline of task transitions and reassignments",
    )

    model_config = ConfigDict(from_attributes=True)
