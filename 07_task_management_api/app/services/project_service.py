"""Service layer handling Project business logic and authorization rules."""

from typing import List, Optional, Sequence, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import (
    DuplicateEntityError,
    EntityNotFoundError,
    PermissionDeniedError,
)
from app.crud.crud_project import project_crud
from app.crud.crud_user import user_crud
from app.models.project import Project, ProjectMember, ProjectMemberRole, ProjectStatus
from app.models.user import User, UserRole
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)


class ProjectService:
    """Encapsulates business operations and permission validations for Projects."""

    @staticmethod
    async def create_project(
        db: AsyncSession,
        project_in: ProjectCreate,
        current_user: User,
    ) -> Project:
        """Create project. Any authenticated member can create projects they own."""
        # Viewers cannot create projects
        if current_user.role == UserRole.VIEWER:
            raise PermissionDeniedError("Viewers are not permitted to create projects.")

        project = await project_crud.create_with_owner(
            db=db,
            obj_in=project_in,
            owner_id=current_user.id,
        )
        return project

    @staticmethod
    async def get_project_detail(
        db: AsyncSession,
        project_id: int,
        current_user: User,
    ) -> ProjectDetailResponse:
        """Fetch project details, validating read permissions and aggregating task stats."""
        project = await project_crud.get_with_details(db, project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check visibility
        if not current_user.is_admin and project.owner_id != current_user.id:
            is_member = await project_crud.is_member(db, project_id, current_user.id)
            if not is_member:
                raise PermissionDeniedError("You do not have permission to view this project.")

        # Aggregate task metrics
        task_counts = await project_crud.get_task_counts(db, project_id)

        # Assemble response
        members_resp = [
            ProjectMemberResponse.model_validate(m) for m in project.members
        ]

        return ProjectDetailResponse(
            id=project.id,
            name=project.name,
            description=project.description,
            status=project.status,
            owner_id=project.owner_id,
            owner=project.owner,
            created_at=project.created_at,
            updated_at=project.updated_at,
            members=members_resp,
            task_counts=task_counts,
        )

    @staticmethod
    async def update_project(
        db: AsyncSession,
        project_id: int,
        project_in: ProjectUpdate,
        current_user: User,
    ) -> Project:
        """Update project. Permitted only to project owner, manager, or admin."""
        project = await project_crud.get(db, project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        # Check authorization
        is_owner = project.owner_id == current_user.id
        is_manager_or_admin = current_user.role in {UserRole.ADMIN, UserRole.MANAGER}
        if not (is_owner or is_manager_or_admin):
            raise PermissionDeniedError("Only the project owner, managers, or admins can update this project.")

        await project_crud.update(db, db_obj=project, obj_in=project_in)
        query = (
            select(Project)
            .where(Project.id == project_id)
            .options(selectinload(Project.owner))
        )
        res = await db.execute(query)
        return res.scalars().first()

    @staticmethod
    async def delete_project(
        db: AsyncSession,
        project_id: int,
        current_user: User,
    ) -> Project:
        """Delete project. Permitted only to project owner or system admin."""
        project = await project_crud.get(db, project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        is_owner = project.owner_id == current_user.id
        if not (is_owner or current_user.is_admin):
            raise PermissionDeniedError("Only the project owner or system administrator can delete this project.")

        return await project_crud.remove(db, id=project_id)

    @staticmethod
    async def add_member(
        db: AsyncSession,
        project_id: int,
        member_in: ProjectMemberCreate,
        current_user: User,
    ) -> ProjectMember:
        """Add user to project. Permitted to project owner, manager, or admin."""
        project = await project_crud.get(db, project_id)
        if not project:
            raise EntityNotFoundError("Project", project_id)

        is_owner = project.owner_id == current_user.id
        is_manager_or_admin = current_user.role in {UserRole.ADMIN, UserRole.MANAGER}
        if not (is_owner or is_manager_or_admin):
            raise PermissionDeniedError("Only the project owner, managers, or admins can manage team members.")

        # Check that user to add exists
        user_to_add = await user_crud.get(db, member_in.user_id)
        if not user_to_add:
            raise EntityNotFoundError("User", member_in.user_id)

        return await project_crud.add_member(
            db=db,
            project_id=project_id,
            user_id=member_in.user_id,
            role=member_in.role,
        )


project_service = ProjectService()
