"""User management endpoints."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy import func, select

from app.api.deps import CurrentAdminDep, CurrentUserDep, SessionDep
from app.core.exceptions import EntityNotFoundError, PermissionDeniedError
from app.crud.crud_user import user_crud
from app.models.user import User, UserRole
from app.schemas.common import PaginatedResponse
from app.schemas.user import UserResponse, UserSummary, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/",
    response_model=PaginatedResponse[UserSummary],
    summary="List all users with pagination",
    description="Retrieves a list of active users. Used for project membership and task assignment.",
)
async def list_users(
    db: SessionDep,
    current_user: CurrentUserDep,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    role: Optional[UserRole] = Query(None, description="Filter by user role"),
) -> PaginatedResponse[UserSummary]:
    """List users for assignment and administration."""
    skip = (page - 1) * limit
    query = select(User).where(User.is_active == True)
    count_query = select(func.count(User.id)).where(User.is_active == True)

    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    total_res = await db.execute(count_query)
    total = total_res.scalar() or 0

    query = query.order_by(User.username.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    items = [UserSummary.model_validate(u) for u in users]
    return PaginatedResponse.create(items=items, total=total, page=page, limit=limit)


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    summary="Get user details by ID",
    description="Fetch a user profile by ID.",
)
async def get_user_by_id(
    user_id: int,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> UserResponse:
    """Fetch user profile."""
    user = await user_crud.get(db, user_id)
    if not user:
        raise EntityNotFoundError("User", user_id)
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile or role",
    description="Users can update their own details. Only Admins can modify user roles and active status.",
)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: SessionDep,
    current_user: CurrentUserDep,
) -> UserResponse:
    """Update profile and manage roles."""
    target_user = await user_crud.get(db, user_id)
    if not target_user:
        raise EntityNotFoundError("User", user_id)

    # If updating role or active status, require Admin
    if user_in.role is not None or user_in.is_active is not None:
        if not current_user.is_admin:
            raise PermissionDeniedError("Only system administrators can modify user roles or active status.")

    # If updating another user's personal details, require Admin
    if target_user.id != current_user.id and not current_user.is_admin:
        raise PermissionDeniedError("You cannot modify another user's account.")

    updated = await user_crud.update(db, db_obj=target_user, obj_in=user_in)
    return updated
