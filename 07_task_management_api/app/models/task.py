"""Task model representing manageable work units."""

from datetime import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.workflow import TaskPriority, TaskStatus
from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.audit_log import TaskAuditLog


class Task(Base, TimestampMixin):
    """Task entity representing a trackable unit of work."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(180), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[TaskStatus] = mapped_column(
        SQLEnum(TaskStatus, name="task_status_enum", native_enum=False),
        default=TaskStatus.TODO,
        nullable=False,
        index=True,
    )
    priority: Mapped[TaskPriority] = mapped_column(
        SQLEnum(TaskPriority, name="task_priority_enum", native_enum=False),
        default=TaskPriority.MEDIUM,
        nullable=False,
        index=True,
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    # Foreign Keys
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    creator_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="tasks",
    )
    assignee: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="assigned_tasks",
        foreign_keys=[assignee_id],
    )
    creator: Mapped["User"] = relationship(
        "User",
        back_populates="created_tasks",
        foreign_keys=[creator_id],
    )
    audit_logs: Mapped[List["TaskAuditLog"]] = relationship(
        "TaskAuditLog",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="TaskAuditLog.created_at.desc()",
    )

    def __repr__(self) -> str:
        return f"<Task id={self.id} title='{self.title[:20]}' status='{self.status.value}'>"
