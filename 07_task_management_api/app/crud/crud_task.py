"""CRUD repository for Task entities, complex filtering, pagination, and audit logging."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from sqlalchemy import asc, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.audit_log import TaskAuditLog
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.user import User
from app.core.workflow import TaskPriority, TaskStatus
from app.schemas.task import TaskCreate, TaskPatch, TaskUpdate


class CRUDTask(CRUDBase[Task, TaskCreate, TaskUpdate]):
    """Task repository handling CRUD, filtering, pagination, and workflow state changes."""

    def __init__(self):
        super().__init__(Task)

    async def get_with_relations(self, db: AsyncSession, task_id: int) -> Optional[Task]:
        """Fetch task with eager-loaded assignee, creator, project, and audit logs."""
        query = (
            select(Task)
            .where(Task.id == task_id)
            .options(
                selectinload(Task.assignee),
                selectinload(Task.creator),
                selectinload(Task.project),
                selectinload(Task.audit_logs).selectinload(TaskAuditLog.changed_by),
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def create_with_creator(
        self,
        db: AsyncSession,
        obj_in: TaskCreate,
        creator_id: int,
    ) -> Task:
        """Create a new task and record the initial creation audit entry."""
        task_data = obj_in.model_dump()
        task_data["creator_id"] = creator_id
        if "status" not in task_data or not task_data["status"]:
            task_data["status"] = TaskStatus.TODO

        db_task = Task(**task_data)
        db.add(db_task)
        await db.flush()

        # Record initial audit entry
        audit_entry = TaskAuditLog(
            task_id=db_task.id,
            changed_by_id=creator_id,
            old_status=None,
            new_status=db_task.status.value,
            notes="Initial task creation",
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(db_task)
        return await self.get_with_relations(db, db_task.id)

    async def get_multi_filtered(
        self,
        db: AsyncSession,
        current_user: User,
        project_id: Optional[int] = None,
        status: Optional[TaskStatus] = None,
        assignee_id: Optional[int] = None,
        priority: Optional[TaskPriority] = None,
        due_date_before: Optional[datetime] = None,
        due_date_after: Optional[datetime] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Task], int]:
        """
        Query tasks applying multi-criteria filters, full-text search, role-based scope,
        custom sorting, and pagination.
        """
        query = select(Task).options(
            selectinload(Task.assignee),
            selectinload(Task.creator),
            selectinload(Task.project),
        )
        count_query = select(func.count(func.distinct(Task.id)))

        # 1. Role-based scoping: non-admins only see tasks in projects they own or belong to
        if not current_user.is_admin:
            accessible_projects_subquery = (
                select(Project.id)
                .where(
                    or_(
                        Project.owner_id == current_user.id,
                        Project.id.in_(
                            select(ProjectMember.project_id).where(
                                ProjectMember.user_id == current_user.id
                            )
                        ),
                    )
                )
            )
            query = query.where(Task.project_id.in_(accessible_projects_subquery))
            count_query = count_query.where(Task.project_id.in_(accessible_projects_subquery))

        # 2. Filter by project_id
        if project_id is not None:
            query = query.where(Task.project_id == project_id)
            count_query = count_query.where(Task.project_id == project_id)

        # 3. Filter by status
        if status is not None:
            query = query.where(Task.status == status)
            count_query = count_query.where(Task.status == status)

        # 4. Filter by assignee_id
        if assignee_id is not None:
            query = query.where(Task.assignee_id == assignee_id)
            count_query = count_query.where(Task.assignee_id == assignee_id)

        # 5. Filter by priority
        if priority is not None:
            query = query.where(Task.priority == priority)
            count_query = count_query.where(Task.priority == priority)

        # 6. Filter by due_date range
        if due_date_before is not None:
            query = query.where(Task.due_date <= due_date_before)
            count_query = count_query.where(Task.due_date <= due_date_before)
        if due_date_after is not None:
            query = query.where(Task.due_date >= due_date_after)
            count_query = count_query.where(Task.due_date >= due_date_after)

        # 7. Search filter on title and description
        if search:
            search_pattern = f"%{search.strip()}%"
            search_clause = or_(
                Task.title.ilike(search_pattern),
                Task.description.ilike(search_pattern),
            )
            query = query.where(search_clause)
            count_query = count_query.where(search_clause)

        # 8. Calculate total filtered count
        count_res = await db.execute(count_query)
        total = count_res.scalar() or 0

        # 9. Sorting
        sort_column_map = {
            "created_at": Task.created_at,
            "due_date": Task.due_date,
            "priority": Task.priority,
            "title": Task.title,
            "status": Task.status,
            "updated_at": Task.updated_at,
        }
        col = sort_column_map.get(sort_by, Task.created_at)
        order_clause = desc(col) if sort_order.lower() == "desc" else asc(col)
        query = query.order_by(order_clause)

        # 10. Pagination
        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        tasks = result.scalars().all()

        return tasks, total

    async def update_status_with_audit(
        self,
        db: AsyncSession,
        task: Task,
        target_status: TaskStatus,
        changed_by_id: int,
        notes: Optional[str] = None,
    ) -> Task:
        """Update task status and append a historical audit record."""
        old_status = task.status.value
        task.status = target_status
        db.add(task)

        audit_entry = TaskAuditLog(
            task_id=task.id,
            changed_by_id=changed_by_id,
            old_status=old_status,
            new_status=target_status.value,
            notes=notes or f"Transitioned from {old_status} to {target_status.value}",
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(task)
        return await self.get_with_relations(db, task.id)

    async def assign_task_with_audit(
        self,
        db: AsyncSession,
        task: Task,
        new_assignee_id: Optional[int],
        changed_by_id: int,
        notes: Optional[str] = None,
    ) -> Task:
        """Assign or reassign task to user and append audit entry."""
        old_assignee_id = task.assignee_id
        task.assignee_id = new_assignee_id
        db.add(task)

        action_msg = f"Assigned to user ID {new_assignee_id}" if new_assignee_id else "Unassigned task"
        full_notes = f"{action_msg}. {notes}" if notes else action_msg

        audit_entry = TaskAuditLog(
            task_id=task.id,
            changed_by_id=changed_by_id,
            old_status=task.status.value,
            new_status=task.status.value,
            notes=full_notes,
        )
        db.add(audit_entry)
        await db.commit()
        await db.refresh(task)
        return await self.get_with_relations(db, task.id)

    async def get_audit_history(
        self,
        db: AsyncSession,
        task_id: int,
    ) -> Sequence[TaskAuditLog]:
        """Fetch audit log timeline for a task ordered from newest to oldest."""
        query = (
            select(TaskAuditLog)
            .where(TaskAuditLog.task_id == task_id)
            .options(selectinload(TaskAuditLog.changed_by))
            .order_by(TaskAuditLog.created_at.desc())
        )
        result = await db.execute(query)
        return result.scalars().all()


task_crud = CRUDTask()
