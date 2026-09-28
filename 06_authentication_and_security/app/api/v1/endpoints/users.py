"""User Management Endpoints protected with Role-Based Access Control."""

import math
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Path, Response, status

from app.api.deps import (
    CurrentAdminUserDep,
    CurrentUserDep,
    PaginationParams,
    SessionDep,
)
from app.crud.crud_user import crud_user
from app.schemas.common import PaginatedResponse
from app.schemas.user import (
    UserCreate,
    UserDetailResponse,
    UserResponse,
    UserUpdate,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create user (Admin Only)",
    description="Allows administrators to directly create new user accounts with specified roles.",
    responses={
        201: {"description": "User created successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin role required"},
        409: {"description": "Email or Username already exists"},
    },
)
async def create_user_admin(
    user_in: UserCreate,
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
) -> UserResponse:
    """Create a new user (Admin only)."""
    existing_email = await crud_user.get_by_email(session, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    existing_username = await crud_user.get_by_username(session, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with username '{user_in.username}' already exists.",
        )

    user = await crud_user.create_with_hash(session, user_in)
    return user


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users (Admin Only)",
    description="Retrieve paginated list of all registered accounts. Restricted to administrators.",
    responses={
        200: {"description": "Paginated users"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin role required"},
    },
)
async def list_users(
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
    pagination: Annotated[PaginationParams, Depends()],
) -> PaginatedResponse[UserResponse]:
    """Retrieve paginated list of users (Admin only)."""
    users, total = await crud_user.get_multi(session, skip=pagination.skip, limit=pagination.limit)
    total_pages = math.ceil(total / pagination.limit) if total > 0 else 0

    return PaginatedResponse[UserResponse](
        total=total,
        page=pagination.page,
        page_size=pagination.limit,
        total_pages=total_pages,
        items=users,
    )


@router.get(
    "/{user_id}",
    response_model=UserDetailResponse,
    summary="Get user by ID",
    description="Retrieve user profile by primary key. Authenticated user can view self; Admin can view any user.",
    responses={
        200: {"description": "User profile with owned products"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Cannot view other users' profiles"},
        404: {"description": "User not found"},
    },
)
async def get_user_by_id(
    session: SessionDep,
    current_user: CurrentUserDep,
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
) -> UserDetailResponse:
    """Fetch user profile by ID."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this user profile.",
        )

    user = await crud_user.get_with_products(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    return user


@router.patch(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user profile",
    description="Partially update user profile. A user can update their own profile; Admin can update any user.",
    responses={
        200: {"description": "User updated successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        404: {"description": "User not found"},
        409: {"description": "Username or Email conflict"},
    },
)
async def update_user(
    session: SessionDep,
    current_user: CurrentUserDep,
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
    user_in: UserUpdate,
) -> UserResponse:
    """Partially update user details."""
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to modify this user account.",
        )

    db_user = await crud_user.get(session, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )

    # Non-admins cannot elevate their own role
    if user_in.role and not current_user.is_admin and user_in.role != db_user.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can modify account roles.",
        )

    # Check for email collision
    if user_in.email and user_in.email != db_user.email:
        existing = await crud_user.get_by_email(session, user_in.email)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{user_in.email}' is already in use.",
            )

    # Check for username collision
    if user_in.username and user_in.username != db_user.username:
        existing = await crud_user.get_by_username(session, user_in.username)
        if existing and existing.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{user_in.username}' is already in use.",
            )

    updated = await crud_user.update(session, db_obj=db_user, obj_in=user_in)
    return updated


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (Admin Only)",
    description="Deletes a user account and cascades deletion to owned products. Strictly restricted to Admin.",
    responses={
        204: {"description": "User deleted successfully"},
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden - Admin role required"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    session: SessionDep,
    admin_user: CurrentAdminUserDep,
    user_id: Annotated[int, Path(..., ge=1, description="User ID")],
) -> Response:
    """Delete user and cascade owned records (Admin only)."""
    db_user = await crud_user.get(session, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )

    await crud_user.remove(session, id=user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
