"""Task service implementing workflow state transitions, RBAC enforcement, and audits."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    EntityNotFoundError,
    InvalidOperationError,
    PermissionDeniedError,
)
from app.core.workflow import TaskStatus, WorkflowEngine
from app.crud.crud_project import project_crud
from app.crud.crud_task import task_crud
from app.crud.crud_user import user_crud
from app.models.task import Task
from app.models.user import User, UserRole
from app.schemas.audit_log import TaskAuditLogResponse
from app.schemas.task import (
    TaskAssignRequest,
    TaskCreate,
    TaskDetailResponse,
    TaskPatch,
    TaskResponse,
    TaskStatusUpdate,
    TaskUpdate,
)


class TaskService:
    """Business operations governing task lifecycles, permissions, and workflow transitions."""

    @staticmethod
    async def create_task(
        db: AsyncSession,
        task_in: TaskCreate,
        current_user: User,
    ) -> Task:
        """Create a new task within a project after verifying project accessibility."""
        if current_user.role == UserRole.VIEWER:
            raise PermissionDeniedError("Viewers are not permitted to create tasks.")

        # Verify project existence
        project = await project_crud.get(db, task_in.project_id)
        if not project:
            raise EntityNotFoundError("Project", task_in.project_id)

        # Verify project access
        if not current_user.is_admin and project.owner_id != current_user.id:
            is_member = await project_crud.is_member(db, task_in.project_id, current_user.id)
            if not is_member and current_user.role != UserRole.MANAGER:
                raise PermissionDeniedError("You do not have access to create tasks in this project.")

        # Verify assignee existence if provided
        if task_in.assignee_id is not None:
            assignee = await user_crud.get(db, task_in.assignee_id)
            if not assignee or not assignee.is_active:
                raise EntityNotFoundError("Assignee User", task_in.assignee_id)

        task = await task_crud.create_with_creator(
            db=db,
            obj_in=task_in,
            creator_id=current_user.id,
        )
        return task

    @staticmethod
    async def get_task_detail(
        db: AsyncSession,
        task_id: int,
        current_user: User,
    ) -> TaskDetailResponse:
        """Fetch full task detail, audit logs, and permitted workflow transitions."""
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        # Check project visibility
        if not current_user.is_admin and task.project.owner_id != current_user.id:
            is_member = await project_crud.is_member(db, task.project_id, current_user.id)
            if not is_member and task.assignee_id != current_user.id and task.creator_id != current_user.id:
                raise PermissionDeniedError("You do not have permission to view this task.")

        # Calculate permitted transitions
        allowed = WorkflowEngine.get_allowed_transitions(task.status)

        # Format audit logs
        audit_logs_resp = [
            TaskAuditLogResponse.model_validate(log) for log in task.audit_logs
        ]

        return TaskDetailResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            project_id=task.project_id,
            assignee_id=task.assignee_id,
            creator_id=task.creator_id,
            created_at=task.created_at,
            updated_at=task.updated_at,
            assignee=task.assignee,
            creator=task.creator,
            allowed_transitions=allowed,
            audit_logs=audit_logs_resp,
        )

    @staticmethod
    async def update_task(
        db: AsyncSession,
        task_id: int,
        task_in: TaskUpdate,
        current_user: User,
    ) -> Task:
        """Full update of task details."""
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        # Check permissions
        if current_user.role == UserRole.VIEWER:
            raise PermissionDeniedError("Viewers are not permitted to modify tasks.")

        is_owner = task.project.owner_id == current_user.id
        is_creator = task.creator_id == current_user.id
        is_assignee = task.assignee_id == current_user.id
        is_mgr_or_admin = current_user.role in {UserRole.ADMIN, UserRole.MANAGER}

        if not (is_owner or is_creator or is_assignee or is_mgr_or_admin):
            raise PermissionDeniedError("You do not have permission to modify this task.")

        # Check assignee if changed
        if task_in.assignee_id is not None and task_in.assignee_id != task.assignee_id:
            assignee = await user_crud.get(db, task_in.assignee_id)
            if not assignee or not assignee.is_active:
                raise EntityNotFoundError("Assignee User", task_in.assignee_id)

        updated_task = await task_crud.update(db, db_obj=task, obj_in=task_in)
        return await task_crud.get_with_relations(db, updated_task.id)

    @staticmethod
    async def patch_task(
        db: AsyncSession,
        task_id: int,
        task_in: TaskPatch,
        current_user: User,
    ) -> Task:
        """Partial update of task details."""
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        if current_user.role == UserRole.VIEWER:
            raise PermissionDeniedError("Viewers are not permitted to modify tasks.")

        is_owner = task.project.owner_id == current_user.id
        is_creator = task.creator_id == current_user.id
        is_assignee = task.assignee_id == current_user.id
        is_mgr_or_admin = current_user.role in {UserRole.ADMIN, UserRole.MANAGER}

        if not (is_owner or is_creator or is_assignee or is_mgr_or_admin):
            raise PermissionDeniedError("You do not have permission to modify this task.")

        if task_in.assignee_id is not None and task_in.assignee_id != task.assignee_id:
            assignee = await user_crud.get(db, task_in.assignee_id)
            if not assignee or not assignee.is_active:
                raise EntityNotFoundError("Assignee User", task_in.assignee_id)

        updated_task = await task_crud.update(db, db_obj=task, obj_in=task_in)
        return await task_crud.get_with_relations(db, updated_task.id)

    @staticmethod
    async def transition_status(
        db: AsyncSession,
        task_id: int,
        status_in: TaskStatusUpdate,
        current_user: User,
    ) -> TaskDetailResponse:
        """
        Execute task workflow status transition with state machine validation and audit recording.
        """
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        # Validate transition using WorkflowEngine
        WorkflowEngine.validate_transition(
            current_status=task.status,
            target_status=status_in.status,
            user_role=current_user.role.value,
            is_task_assignee=(task.assignee_id == current_user.id),
            is_task_creator=(task.creator_id == current_user.id),
            is_project_owner=(task.project.owner_id == current_user.id),
        )

        # Perform transition and create audit record
        updated_task = await task_crud.update_status_with_audit(
            db=db,
            task=task,
            target_status=status_in.status,
            changed_by_id=current_user.id,
            notes=status_in.notes,
        )

        return await TaskService.get_task_detail(db, updated_task.id, current_user)

    @staticmethod
    async def assign_task(
        db: AsyncSession,
        task_id: int,
        assign_in: TaskAssignRequest,
        current_user: User,
    ) -> TaskDetailResponse:
        """Assign or reassign task with privilege verification and audit entry."""
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        # Privilege check: only Project Owner, Manager, or Admin can assign/reassign
        is_owner = task.project.owner_id == current_user.id
        is_mgr_or_admin = current_user.role in {UserRole.ADMIN, UserRole.MANAGER}
        if not (is_owner or is_mgr_or_admin):
            raise PermissionDeniedError("Only the project owner, managers, or admins can reassign tasks.")

        # Check target user
        if assign_in.assignee_id is not None:
            assignee = await user_crud.get(db, assign_in.assignee_id)
            if not assignee or not assignee.is_active:
                raise EntityNotFoundError("Assignee User", assign_in.assignee_id)

        updated_task = await task_crud.assign_task_with_audit(
            db=db,
            task=task,
            new_assignee_id=assign_in.assignee_id,
            changed_by_id=current_user.id,
            notes=assign_in.notes,
        )

        return await TaskService.get_task_detail(db, updated_task.id, current_user)

    @staticmethod
    async def delete_task(
        db: AsyncSession,
        task_id: int,
        current_user: User,
    ) -> Task:
        """Delete task. Permitted to task creator, project owner, or system admin."""
        task = await task_crud.get_with_relations(db, task_id)
        if not task:
            raise EntityNotFoundError("Task", task_id)

        is_owner = task.project.owner_id == current_user.id
        is_creator = task.creator_id == current_user.id
        if not (is_owner or is_creator or current_user.is_admin):
            raise PermissionDeniedError("Only the task creator, project owner, or admin can delete this task.")

        return await task_crud.remove(db, id=task_id)


task_service = TaskService()
