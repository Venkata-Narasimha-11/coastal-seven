"""Project model and membership association table."""

from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlalchemy import (
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.task import Task


class ProjectStatus(str, Enum):
    """Lifecycle statuses for a project."""
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectMemberRole(str, Enum):
    """Member roles within a project."""
    LEAD = "lead"
    CONTRIBUTOR = "contributor"
    OBSERVER = "observer"


class ProjectMember(Base):
    """Association entity linking users to projects with a project-specific role."""

    __tablename__ = "project_members"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user_member"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role: Mapped[ProjectMemberRole] = mapped_column(
        SQLEnum(ProjectMemberRole, name="project_member_role_enum", native_enum=False),
        default=ProjectMemberRole.CONTRIBUTOR,
        nullable=False,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="members")
    user: Mapped["User"] = relationship("User", back_populates="project_memberships")


class Project(Base, TimestampMixin):
    """Project entity organizing collaborative tasks."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ProjectStatus] = mapped_column(
        SQLEnum(ProjectStatus, name="project_status_enum", native_enum=False),
        default=ProjectStatus.ACTIVE,
        nullable=False,
        index=True,
    )
    owner_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Relationships
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_projects",
        foreign_keys=[owner_id],
    )
    members: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="project",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Project id={self.id} name='{self.name}' status='{self.status.value}'>"
