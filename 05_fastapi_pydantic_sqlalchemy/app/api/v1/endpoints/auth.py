"""Authentication and JWT Token Generation Endpoints."""

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.deps import SessionDep
from app.core.config import settings
from app.core.security import create_access_token, decode_access_token
from app.crud.crud_user import crud_user
from app.models.user import User
from app.schemas.auth import LoginRequest, Token
from app.schemas.user import UserResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter JWT Bearer access token only (no username, password, or client credentials needed).",
    auto_error=False,
)

oauth2_scheme = bearer_scheme


async def get_current_user(
    request: Request,
    session: SessionDep,
    auth: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> User:
    """Dependency to retrieve and validate currently authenticated user from JWT Bearer token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    token: Optional[str] = None
    if auth and auth.credentials:
        token = auth.credentials
    else:
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            elif len(parts) == 1:
                token = parts[0]

    if not token:
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    user_id_str: str = payload.get("sub")
    if not user_id_str:
        raise credentials_exception

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise credentials_exception

    user = await crud_user.get(session, user_id)
    if not user:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user account.",
        )
    return user


CurrentUserDep = Annotated[User, Depends(get_current_user)]


@router.post(
    "/login",
    response_model=Token,
    summary="User Login / Issue JWT Access Token",
    description="Authenticates user credentials against stored bcrypt hash and returns a signed JWT bearer token.",
    responses={
        200: {"description": "Authentication successful, token issued"},
        401: {"description": "Incorrect email or password"},
        400: {"description": "Inactive user account"},
    },
)
async def login(
    credentials: LoginRequest,
    session: SessionDep,
) -> Token:
    """Authenticate user and issue JWT access token."""
    user = await crud_user.authenticate(
        session,
        email=credentials.email,
        password=credentials.password,
    )
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

    access_token = create_access_token(subject=user.id)
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
    )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current Authenticated User Profile",
    description="Extracts and verifies the JWT token from the Authorization header and returns the user profile.",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Missing, invalid, or expired bearer token"},
    },
)
async def get_me(
    current_user: CurrentUserDep,
) -> UserResponse:
    """Return currently authenticated user profile."""
    return current_user
