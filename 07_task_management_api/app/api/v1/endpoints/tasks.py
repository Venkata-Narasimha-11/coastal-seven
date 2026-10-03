"""Task management endpoints supporting CRUD, filtering, pagination, and status workflows."""

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUserDep, SessionDep
from app.core.workflow import TaskPriority, TaskStatus
from app.crud.crud_task import task_crud
from app.schemas.audit_log import TaskAuditLogResponse
from app.schemas.common import PaginatedResponse
from app.schemas.task import (
    TaskAssignRequest,
    TaskCreate,
    TaskDetailResponse,
    TaskPatch,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)
from app.services.task_service import task_service

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
    description="Creates a task within a specified project. Automatically logs initial audit entry.",
)
async def create_task(
    task_in: TaskCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskResponse:
    """Create a new task."""
    task = await task_service.create_task(
        db=db,
        task_in=task_in,
        current_user=current_user,
    )
    return task


@router.get(
    "/",
    response_model=PaginatedResponse[TaskResponse],
    summary="List tasks with multi-criteria filtering, search, sorting, and pagination",
    description=(
        "Filters tasks by status, assignee, project, priority, and due date range. "
        "Supports search across title/description, custom sorting, and pagination."
    ),
)
async def list_tasks(
    db: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1, description="Page number (1-indexed)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[TaskStatus] = Query(None, description="Filter by status (todo, in_progress, review, completed, cancelled)"),
    assignee_id: Optional[int] = Query(None, description="Filter by assigned user ID"),
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    priority: Optional[TaskPriority] = Query(None, description="Filter by priority (low, medium, high, urgent)"),
    due_date_before: Optional[datetime] = Query(None, description="Tasks due on or before this timestamp"),
    due_date_after: Optional[datetime] = Query(None, description="Tasks due on or after this timestamp"),
    search: Optional[str] = Query(None, description="Search term in title or description"),
    sort_by: str = Query("created_at", description="Field to sort by (created_at, due_date, priority, title, status)"),
    sort_order: str = Query("desc", pattern=r"^(asc|desc)$", description="Sort direction (asc or desc)"),
) -> PaginatedResponse[TaskResponse]:
    """List tasks with dynamic filtering and pagination."""
    skip = (page - 1) * limit
    tasks, total = await task_crud.get_multi_filtered(
        db=db,
        current_user=current_user,
        project_id=project_id,
        status=status,
        assignee_id=assignee_id,
        priority=priority,
        due_date_before=due_date_before,
        due_date_after=due_date_after,
        search=search,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit,
    )

    items = [TaskResponse.model_validate(t) for t in tasks]
    return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)


@router.get(
    "/{task_id}",
    response_model=TaskDetailResponse,
    summary="Get task details with allowable workflow transitions and audit history",
    description="Returns detailed task metadata, permissible next status options, and the audit log timeline.",
)
async def get_task(
    task_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskDetailResponse:
    """Get single task details."""
    return await task_service.get_task_detail(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Full update of task details",
    description="Updates task title, description, priority, due date, and assignee.",
)
async def update_task(
    task_id: int,
    task_in: TaskUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskResponse:
    """Update task details."""
    return await task_service.update_task(
        db=db,
        task_id=task_id,
        task_in=task_in,
        current_user=current_user,
    )


@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partial update of task fields",
    description="Partially updates task fields without overwriting omitted attributes.",
)
async def patch_task(
    task_id: int,
    task_in: TaskPatch,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskResponse:
    """Partial update of task."""
    return await task_service.patch_task(
        db=db,
        task_id=task_id,
        task_in=task_in,
        current_user=current_user,
    )


@router.patch(
    "/{task_id}/status",
    response_model=TaskDetailResponse,
    summary="Transition task workflow status",
    description=(
        "Executes a state machine status transition. Validates allowable transitions "
        "(e.g., todo -> in_progress -> review -> completed) and checks user permissions."
    ),
)
async def transition_task_status(
    task_id: int,
    status_in: TaskStatusUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskDetailResponse:
    """Transition task status with state machine enforcement."""
    return await task_service.transition_status(
        db=db,
        task_id=task_id,
        status_in=status_in,
        current_user=current_user,
    )


@router.patch(
    "/{task_id}/assign",
    response_model=TaskDetailResponse,
    summary="Assign or reassign a task",
    description="Assigns or reassigns task to a team member. Permitted to project owner, manager, or admin.",
)
async def assign_task(
    task_id: int,
    assign_in: TaskAssignRequest,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> TaskDetailResponse:
    """Assign or reassign task."""
    return await task_service.assign_task(
        db=db,
        task_id=task_id,
        assign_in=assign_in,
        current_user=current_user,
    )


@router.get(
    "/{task_id}/history",
    response_model=List[TaskAuditLogResponse],
    summary="Get task audit history trail",
    description="Returns chronological audit logs showing status changes and reassignments.",
)
async def get_task_history(
    task_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> List[TaskAuditLogResponse]:
    """Retrieve audit timeline for a task."""
    # Ensure user has access
    await task_service.get_task_detail(db, task_id, current_user)
    logs = await task_crud.get_audit_history(db, task_id)
    return [TaskAuditLogResponse.model_validate(log) for log in logs]


@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
    description="Deletes a task and its audit history. Permitted to creator, project owner, or admin.",
)
async def delete_task(
    task_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> Response:
    """Delete task."""
    await task_service.delete_task(
        db=db,
        task_id=task_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
