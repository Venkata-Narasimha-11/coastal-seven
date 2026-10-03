"""Authentication endpoints for user registration, token generation, and refresh."""

from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError

from app.api.deps import CurrentUserDep, SessionDep
from app.core.config import settings
from app.core.exceptions import (
    AuthenticationError,
    DuplicateEntityError,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.crud.crud_user import user_crud
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest,
    RefreshTokenRequest,
    RegisterRequest,
    Token,
)
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
    description="Register a new user with username, email, full name, password, and optional role.",
)
async def register_user(
    db: SessionDep,
    user_in: RegisterRequest,
) -> UserResponse:
    """Register a new user, verifying uniqueness of username and email."""
    # Check if username exists
    existing_username = await user_crud.get_by_username(db, user_in.username)
    if existing_username:
        raise DuplicateEntityError("User", "username", user_in.username)

    # Check if email exists
    existing_email = await user_crud.get_by_email(db, user_in.email)
    if existing_email:
        raise DuplicateEntityError("User", "email", user_in.email)

    # Prevent self-registering as ADMIN unless allowed
    assigned_role = user_in.role or UserRole.DEVELOPER
    if assigned_role == UserRole.ADMIN:
        # If this is the first user, allow admin bootstrap, otherwise default to developer
        total_users = await user_crud.count(db)
        if total_users > 0:
            assigned_role = UserRole.DEVELOPER

    user_create = UserCreate(
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=assigned_role,
    )
    user = await user_crud.create(db, obj_in=user_create)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Authenticate and obtain JWT access & refresh tokens (JSON)",
    description="Authenticates via JSON payload and returns signed JWT access & refresh tokens.",
)
async def login_json(
    db: SessionDep,
    credentials: LoginRequest,
) -> Token:
    """JSON credentials login endpoint."""
    user = await user_crud.authenticate(
        db,
        username_or_email=credentials.username,
        password=credentials.password,
    )
    if not user:
        raise AuthenticationError("Incorrect username/email or password.")

    access_token = create_access_token(
        subject=user.username,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(subject=user.username)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 Password Grant (Swagger UI Login)",
    description="Standard OAuth2 form urlencoded endpoint allowing Swagger UI 'Authorize' button to function.",
)
async def login_form(
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    """Form login endpoint compliant with OAuth2 specification."""
    user = await user_crud.authenticate(
        db,
        username_or_email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise AuthenticationError("Incorrect username or password.")

    access_token = create_access_token(
        subject=user.username,
        role=user.role.value,
    )
    refresh_token = create_refresh_token(subject=user.username)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh access token using a valid refresh token",
    description="Exchanges a valid JWT refresh token for a newly signed access token.",
)
async def refresh_access_token(
    db: SessionDep,
    refresh_in: RefreshTokenRequest,
) -> Token:
    """Exchange refresh token for updated access token."""
    try:
        payload = decode_refresh_token(refresh_in.refresh_token)
        username = payload.get("sub")
        if not username:
            raise AuthenticationError("Invalid refresh token payload.")
    except (JWTError, Exception):
        raise AuthenticationError("Invalid or expired refresh token.")

    user = await user_crud.get_by_username(db, username=username)
    if not user or not user.is_active:
        raise AuthenticationError("User is no longer active.")

    access_token = create_access_token(
        subject=user.username,
        role=user.role.value,
    )
    # Issue a fresh refresh token as well (token rotation)
    new_refresh_token = create_refresh_token(subject=user.username)

    return Token(
        access_token=access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile",
    description="Returns the profile information of the user identified by Bearer token.",
)
async def get_current_user_profile(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Return profile of current active user."""
    return current_user
