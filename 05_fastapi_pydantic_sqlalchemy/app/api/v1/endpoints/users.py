"""FastAPI User Endpoints implementing complete CRUD operations."""

import math
from typing import Annotated, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from app.api.deps import PaginationParams, SessionDep
from app.crud.crud_product import crud_product
from app.crud.crud_user import crud_user
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductSummary
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
    summary="Register a new user",
    description="Creates a new user record with encrypted password. Requires unique email and username.",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "Validation failure or password mismatch"},
        409: {"description": "Email or username already registered"},
    },
)
async def create_user(
    user_in: UserCreate,
    session: SessionDep,
) -> UserResponse:
    """Create a new user in the database."""
    # Check if email is already taken
    existing_email = await crud_user.get_by_email(session, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"User with email '{user_in.email}' already exists.",
        )

    # Check if username is already taken
    existing_username = await crud_user.get_by_username(session, user_in.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Username '{user_in.username}' is already taken.",
        )

    user = await crud_user.create_user(session, user_in)
    return user


@router.get(
    "",
    response_model=PaginatedResponse[UserResponse],
    summary="List all users with pagination",
    description="Retrieve a paginated list of registered users with optional active status filtering.",
)
async def list_users(
    session: SessionDep,
    pagination: Annotated[PaginationParams, Depends()],
    is_active: Optional[bool] = Query(
        None,
        description="Filter users by active/inactive status",
    ),
) -> PaginatedResponse[UserResponse]:
    """Retrieve users with pagination and optional filtering."""
    users, total = await crud_user.get_multi_filtered(
        session,
        skip=pagination.skip,
        limit=pagination.limit,
        is_active=is_active,
    )

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
    summary="Get user details by ID",
    description="Retrieve full user profile details including their catalog products.",
    responses={
        200: {"description": "User profile with nested products"},
        404: {"description": "User not found"},
    },
)
async def get_user_by_id(
    session: SessionDep,
    user_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the user")],
) -> UserDetailResponse:
    """Fetch user by ID with loaded products."""
    user = await crud_user.get_with_products(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    summary="Update user details (Full/Partial)",
    description="Updates existing user profile attributes. Password will be re-hashed if provided.",
    responses={
        200: {"description": "User updated successfully"},
        404: {"description": "User not found"},
        409: {"description": "Email or username collision"},
    },
)
async def update_user(
    session: SessionDep,
    user_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the user")],
    user_in: UserUpdate,
) -> UserResponse:
    """Update user by ID."""
    db_user = await crud_user.get(session, user_id)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )

    # Check email uniqueness if changing email
    if user_in.email and user_in.email != db_user.email:
        existing = await crud_user.get_by_email(session, user_in.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Email '{user_in.email}' is already in use.",
            )

    # Check username uniqueness if changing username
    if user_in.username and user_in.username != db_user.username:
        existing = await crud_user.get_by_username(session, user_in.username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Username '{user_in.username}' is already taken.",
            )

    updated_user = await crud_user.update_user(session, db_user, user_in)
    return updated_user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user",
    description="Removes a user from the system and cascades deletion to their owned products.",
    responses={
        204: {"description": "User successfully deleted"},
        404: {"description": "User not found"},
    },
)
async def delete_user(
    session: SessionDep,
    user_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the user")],
) -> None:
    """Delete user by ID."""
    deleted_user = await crud_user.remove(session, user_id)
    if not deleted_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    return None


@router.get(
    "/{user_id}/products",
    response_model=List[ProductSummary],
    summary="List products owned by user",
    description="Fetch a list of all products belonging to a specific user.",
    responses={
        200: {"description": "List of products owned by the user"},
        404: {"description": "User not found"},
    },
)
async def list_user_products(
    session: SessionDep,
    user_id: Annotated[int, Path(..., ge=1, description="Unique primary key of the user")],
) -> List[ProductSummary]:
    """Retrieve all products created/owned by a given user."""
    user = await crud_user.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} was not found.",
        )
    products, _ = await crud_product.get_multi_by_owner(session, owner_id=user_id, limit=200)
    return products
