"""Schemas package aggregating all validation and serialization contracts."""
from app.schemas.audit_log import TaskAuditLogResponse
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
    TokenPayload,
)
from app.schemas.common import (
    ApiResponse,
    HealthCheckResponse,
    PaginatedResponse,
    PaginationParams,
)
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
    TaskCountSummary,
)
from app.schemas.task import (
    TaskAssignRequest,
    TaskCreate,
    TaskDetailResponse,
    TaskPatch,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.schemas.user import (
    UserCreate,
    UserResponse,
    UserSummary,
    UserUpdate,
)

__all__ = [
    "ApiResponse",
    "HealthCheckResponse",
    "PaginationParams",
    "PaginatedResponse",
    "Token",
    "TokenPayload",
    "LoginRequest",
    "RegisterRequest",
    "RefreshTokenRequest",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserSummary",
    "ProjectCreate",
    "ProjectUpdate",
    "ProjectResponse",
    "ProjectDetailResponse",
    "ProjectMemberCreate",
    "ProjectMemberResponse",
    "TaskCountSummary",
    "TaskCreate",
    "TaskUpdate",
    "TaskPatch",
    "TaskStatusUpdate",
    "TaskAssignRequest",
    "TaskResponse",
    "TaskDetailResponse",
    "TaskAuditLogResponse",
]
