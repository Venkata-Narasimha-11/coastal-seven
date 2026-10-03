"""CRUD repository for Project management and memberships."""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectStatus
from app.models.task import Task
from app.models.user import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate, TaskCountSummary


class CRUDProject(CRUDBase[Project, ProjectCreate, ProjectUpdate]):
    """Project repository with role-scoped querying and task metrics."""

    def __init__(self):
        super().__init__(Project)

    async def get_with_details(self, db: AsyncSession, project_id: int) -> Optional[Project]:
        """Fetch project eager loading owner and members with their user records."""
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(
                selectinload(Project.owner),
                selectinload(Project.members).selectinload(ProjectMember.user),
            )
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_task_counts(self, db: AsyncSession, project_id: int) -> TaskCountSummary:
        """Calculate counts of tasks grouped by status for a project."""
        query = (
            select(Task.status, func.count(Task.id))
            .where(Task.project_id == project_id)
            .group_by(Task.status)
        )
        result = await db.execute(query)
        counts = {status: count for status, count in result.all()}

        summary = TaskCountSummary(
            total=sum(counts.values()),
            todo=counts.get("todo", 0),
            in_progress=counts.get("in_progress", 0),
            review=counts.get("review", 0),
            completed=counts.get("completed", 0),
            cancelled=counts.get("cancelled", 0),
        )
        return summary

    async def get_multi_scoped(
        self,
        db: AsyncSession,
        current_user: User,
        status: Optional[ProjectStatus] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 10,
    ) -> Tuple[Sequence[Project], int]:
        """
        Fetch paginated projects visible to current user based on RBAC:
        - Admin: can see all projects
        - Manager / Developer / Viewer: see projects they own or are members of
        """
        query = select(Project).options(selectinload(Project.owner))
        count_query = select(func.count(func.distinct(Project.id)))

        # Role filtering
        if not current_user.is_admin:
            # Join with project_members for membership visibility
            visibility_filter = or_(
                Project.owner_id == current_user.id,
                Project.id.in_(
                    select(ProjectMember.project_id).where(ProjectMember.user_id == current_user.id)
                ),
            )
            query = query.where(visibility_filter)
            count_query = count_query.where(visibility_filter)

        # Status filter
        if status:
            query = query.where(Project.status == status)
            count_query = count_query.where(Project.status == status)

        # Search filter
        if search:
            search_pattern = f"%{search.strip()}%"
            search_filter = or_(
                Project.name.ilike(search_pattern),
                Project.description.ilike(search_pattern),
            )
            query = query.where(search_filter)
            count_query = count_query.where(search_filter)

        # Count total
        count_result = await db.execute(count_query)
        total = count_result.scalar() or 0

        # Execute paginated query
        query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        result = await db.execute(query)
        projects = result.scalars().all()

        return projects, total

    async def create_with_owner(
        self,
        db: AsyncSession,
        obj_in: ProjectCreate,
        owner_id: int,
    ) -> Project:
        """Create project with assigned owner and add owner as Lead member."""
        project_data = obj_in.model_dump()
        project_data["owner_id"] = owner_id
        db_project = Project(**project_data)
        db.add(db_project)
        await db.flush()

        # Add owner to project_members as LEAD
        lead_member = ProjectMember(
            project_id=db_project.id,
            user_id=owner_id,
            role=ProjectMemberRole.LEAD,
        )
        db.add(lead_member)
        await db.commit()
        
        # Load owner relationship for clean serialization
        query = select(Project).where(Project.id == db_project.id).options(selectinload(Project.owner))
        return (await db.execute(query)).scalars().first()

    async def add_member(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
        role: ProjectMemberRole = ProjectMemberRole.CONTRIBUTOR,
    ) -> ProjectMember:
        """Add user to project membership."""
        # Check if already a member
        query = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        existing = (await db.execute(query)).scalars().first()
        if existing:
            existing.role = role
            await db.commit()
            member_id = existing.id
        else:
            member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
            db.add(member)
            await db.commit()
            member_id = member.id

        # Load user relation for response model
        load_q = (
            select(ProjectMember)
            .where(ProjectMember.id == member_id)
            .options(selectinload(ProjectMember.user))
        )
        return (await db.execute(load_q)).scalars().first()

    async def remove_member(
        self,
        db: AsyncSession,
        project_id: int,
        user_id: int,
    ) -> bool:
        """Remove member from project."""
        query = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member = (await db.execute(query)).scalars().first()
        if member:
            await db.delete(member)
            await db.commit()
            return True
        return False

    async def is_member(self, db: AsyncSession, project_id: int, user_id: int) -> bool:
        """Check if user is a member of the project."""
        query = select(func.count(ProjectMember.id)).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        res = await db.execute(query)
        return (res.scalar() or 0) > 0


project_crud = CRUDProject()
