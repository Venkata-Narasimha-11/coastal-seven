"""Project schemas for validation and API responses."""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.models.project import ProjectMemberRole, ProjectStatus
from app.schemas.user import UserSummary


class ProjectBase(BaseModel):
    """Base project schema with core attributes."""
    name: str = Field(min_length=2, max_length=120, description="Project name")
    description: Optional[str] = Field(default=None, max_length=2000, description="Project overview")
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, description="Lifecycle status")


class ProjectCreate(ProjectBase):
    """Payload to create a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Payload to update an existing project."""
    name: Optional[str] = Field(default=None, min_length=2, max_length=120)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: Optional[ProjectStatus] = None


class ProjectMemberCreate(BaseModel):
    """Payload to add a team member to a project."""
    user_id: int
    role: ProjectMemberRole = ProjectMemberRole.CONTRIBUTOR


class ProjectMemberResponse(BaseModel):
    """Project membership information."""
    id: int
    user_id: int
    role: ProjectMemberRole
    joined_at: datetime
    user: Optional[UserSummary] = None

    model_config = ConfigDict(from_attributes=True)


class TaskCountSummary(BaseModel):
    """Summary metrics of task statuses within a project."""
    total: int = 0
    todo: int = 0
    in_progress: int = 0
    review: int = 0
    completed: int = 0
    cancelled: int = 0


class ProjectResponse(ProjectBase):
    """Standard project response model."""
    id: int
    owner_id: int
    owner: Optional[UserSummary] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProjectDetailResponse(ProjectResponse):
    """Detailed project representation with membership and task metrics."""
    members: List[ProjectMemberResponse] = []
    task_counts: TaskCountSummary = Field(default_factory=TaskCountSummary)

    model_config = ConfigDict(from_attributes=True)
