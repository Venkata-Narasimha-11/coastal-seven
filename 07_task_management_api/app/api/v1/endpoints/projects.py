"""Project management and team collaboration endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, Query, Response, status

from app.api.deps import CurrentUserDep, SessionDep
from app.crud.crud_project import project_crud
from app.models.project import ProjectMemberRole, ProjectStatus
from app.schemas.common import PaginatedResponse
from app.schemas.project import (
    ProjectCreate,
    ProjectDetailResponse,
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectResponse,
    ProjectUpdate,
)
from app.services.project_service import project_service

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project",
    description="Creates a new project. The creator becomes the owner and is automatically assigned as Lead member.",
)
async def create_project(
    project_in: ProjectCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> ProjectResponse:
    """Create a new project."""
    project = await project_service.create_project(
        db=db,
        project_in=project_in,
        current_user=current_user,
    )
    return project


@router.get(
    "/",
    response_model=PaginatedResponse[ProjectResponse],
    summary="List accessible projects with pagination and filtering",
    description="Returns projects accessible to the user (Admins see all; members see owned or enrolled projects).",
)
async def list_projects(
    db: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    search: Optional[str] = Query(None, description="Search term matching project name or description"),
) -> PaginatedResponse[ProjectResponse]:
    """List accessible projects."""
    skip = (page - 1) * limit
    projects, total = await project_crud.get_multi_scoped(
        db=db,
        current_user=current_user,
        status=status,
        search=search,
        skip=skip,
        limit=limit,
    )

    items = [ProjectResponse.model_validate(p) for p in projects]
    return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)


@router.get(
    "/{project_id}",
    response_model=ProjectDetailResponse,
    summary="Get project details with task counts and team members",
    description="Returns detailed project metadata, current team members, and real-time task status metrics.",
)
async def get_project(
    project_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> ProjectDetailResponse:
    """Get project details."""
    return await project_service.get_project_detail(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    summary="Update project details",
    description="Updates project name, description, or status. Permitted to project owner, managers, or admins.",
)
async def update_project(
    project_id: int,
    project_in: ProjectUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> ProjectResponse:
    """Update project."""
    project = await project_service.update_project(
        db=db,
        project_id=project_id,
        project_in=project_in,
        current_user=current_user,
    )
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a project",
    description="Deletes a project and all associated tasks and memberships. Permitted to owner or admin.",
)
async def delete_project(
    project_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> Response:
    """Delete project."""
    await project_service.delete_project(
        db=db,
        project_id=project_id,
        current_user=current_user,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a team member to a project",
    description="Adds or updates a team member's role in the project. Permitted to owner, manager, or admin.",
)
async def add_project_member(
    project_id: int,
    member_in: ProjectMemberCreate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> ProjectMemberResponse:
    """Add member to project."""
    member = await project_service.add_member(
        db=db,
        project_id=project_id,
        member_in=member_in,
        current_user=current_user,
    )
    return member
