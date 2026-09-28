"""Authentication and Token Management Endpoints for Day 6."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUserDep, SessionDep, oauth2_scheme
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.crud.crud_user import crud_user
from app.schemas.auth import LoginRequest, RefreshTokenRequest, Token, UserRegister
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ------------------------------------------------------------------------------
# 4. AUTHENTICATION ENDPOINTS: /register, /login, /me, /refresh
# ------------------------------------------------------------------------------

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User Registration",
    description="Registers a new user account with hashed password storage using passlib + bcrypt.",
    responses={
        201: {"description": "User successfully registered"},
        400: {"description": "Invalid input data or password mismatch"},
        409: {"description": "Username or Email already registered"},
    },
)
async def register(
    user_in: UserRegister,
    session: SessionDep,
) -> UserResponse:
    """Register a new user account."""
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


@router.post(
    "/login",
    response_model=Token,
    summary="User Login / Issue JWT Access & Refresh Tokens",
    description=(
        "Authenticates credentials and issues signed JWT access and refresh tokens. "
        "Supports both application/json payloads and standard OAuth2 application/x-www-form-urlencoded forms."
    ),
    responses={
        200: {"description": "Authentication successful, tokens issued"},
        400: {"description": "Inactive user account or malformed request"},
        401: {"description": "Incorrect email/username or password"},
    },
)
async def login(
    request: Request,
    session: SessionDep,
) -> Token:
    """Authenticate credentials and issue JWT access and refresh tokens."""
    content_type = request.headers.get("content-type", "")
    identifier: Optional[str] = None
    password: Optional[str] = None

    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form_data = await request.form()
        identifier = str(form_data.get("username", "")).strip()
        password = str(form_data.get("password", ""))
    else:
        try:
            body = await request.json()
            identifier = str(body.get("email") or body.get("username", "")).strip()
            password = str(body.get("password", ""))
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request body. Expected JSON or form data.",
            )

    if not identifier or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Identifier (email/username) and password are required.",
        )

    user = await crud_user.authenticate(session, identifier=identifier, password=password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is inactive. Please contact support.",
        )

    roles = ["admin"] if user.is_admin else ["user"]
    access_token = create_access_token(
        subject=user.id,
        roles=roles,
        extra_claims={"email": user.email, "role": user.role},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 Standard Password Form Login",
    description="Standard OAuth2 form login for Swagger UI Authorize modal compatibility.",
    include_in_schema=False,
)
async def login_oauth2_form(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """OAuth2 password specification form login."""
    user = await crud_user.authenticate(
        session, identifier=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    roles = ["admin"] if user.is_admin else ["user"]
    access_token = create_access_token(
        subject=user.id,
        roles=roles,
        extra_claims={"email": user.email, "role": user.role},
    )
    refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current Authenticated User Profile",
    description="Validates Bearer access token and returns currently authenticated user details.",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Missing, invalid, or expired Bearer token"},
    },
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Return currently authenticated user profile."""
    return current_user


@router.post(
    "/refresh",
    response_model=Token,
    summary="Refresh Access Token",
    description="Exchanges a valid JWT refresh token for a newly signed access token and rotated refresh token.",
    responses={
        200: {"description": "Token refreshed successfully"},
        400: {"description": "Inactive user account"},
        401: {"description": "Invalid, expired, or wrong type token"},
    },
)
async def refresh_token(
    refresh_payload: RefreshTokenRequest,
    session: SessionDep,
) -> Token:
    """Validate refresh token and issue new token pair."""
    token_str = refresh_payload.refresh_token.strip()
    payload = decode_refresh_token(token_str)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not extract user identity from token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Malformed token identity claim.",
        )

    user = await crud_user.get(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )

    roles = ["admin"] if user.is_admin else ["user"]
    new_access_token = create_access_token(
        subject=user.id,
        roles=roles,
        extra_claims={"email": user.email, "role": user.role},
    )
    new_refresh_token = create_refresh_token(subject=user.id)

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
