"""User model and role definitions for RBAC."""

from enum import Enum
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, Enum as SQLEnum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.project import Project, ProjectMember
    from app.models.task import Task
    from app.models.audit_log import TaskAuditLog


class UserRole(str, Enum):
    """Hierarchical user roles for authorization."""
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class User(Base, TimestampMixin):
    """User entity supporting authentication and RBAC."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role_enum", native_enum=False),
        default=UserRole.DEVELOPER,
        nullable=False,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    owned_projects: Mapped[List["Project"]] = relationship(
        "Project",
        back_populates="owner",
        cascade="all, delete-orphan",
        foreign_keys="Project.owner_id",
    )
    assigned_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="assignee",
        foreign_keys="Task.assignee_id",
    )
    created_tasks: Mapped[List["Task"]] = relationship(
        "Task",
        back_populates="creator",
        cascade="all, delete-orphan",
        foreign_keys="Task.creator_id",
    )
    project_memberships: Mapped[List["ProjectMember"]] = relationship(
        "ProjectMember",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    audit_logs: Mapped[List["TaskAuditLog"]] = relationship(
        "TaskAuditLog",
        back_populates="changed_by",
    )

    @property
    def is_admin(self) -> bool:
        """Check if user is administrator."""
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self) -> bool:
        """Check if user has manager-level privileges."""
        return self.role in {UserRole.ADMIN, UserRole.MANAGER}

    def __repr__(self) -> str:
        return f"<User id={self.id} username='{self.username}' role='{self.role.value}'>"
