"""FastAPI dependencies for database sessions, Bearer JWT authentication, and RBAC enforcement."""

from typing import Annotated, Callable, List, Optional
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthenticationError, PermissionDeniedError
from app.core.security import decode_access_token
from app.crud.crud_user import user_crud
from app.db.session import get_async_db
from app.models.user import User, UserRole

# HTTPBearer scheme: Swagger UI prompt only requires entering the Bearer JWT token (no username/password form)
bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter JWT Bearer token only (no username, password, or client credentials needed).",
    auto_error=False,
)

# Export alias for compatibility
oauth2_scheme = bearer_scheme


async def get_current_user(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_async_db)],
    auth: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> User:
    """Validate Bearer token and retrieve the currently authenticated user."""
    token: Optional[str] = None
    if auth and auth.credentials:
        token = auth.credentials
    else:
        # Fallback to direct Authorization header check
        auth_header = request.headers.get("Authorization")
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0].lower() == "bearer":
                token = parts[1]
            elif len(parts) == 1:
                token = parts[0]

    if not token:
        raise AuthenticationError("Not authenticated. Please provide a Bearer token.")

    try:
        payload = decode_access_token(token)
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Token payload missing subject claim.")
    except (JWTError, Exception) as e:
        raise AuthenticationError(f"Could not validate credentials: {str(e)}")

    user = await user_crud.get_by_username(db, username=username)
    if not user:
        # Fallback to checking by ID if sub is numeric
        if username.isdigit():
            user = await user_crud.get(db, int(username))

    if not user:
        raise AuthenticationError("Authenticated user no longer exists.")

    if not user.is_active:
        raise PermissionDeniedError("User account is disabled or deactivated.")

    return user


def require_roles(allowed_roles: List[UserRole]) -> Callable:
    """Dependency factory checking that user holds at least one of the specified roles."""

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            role_names = [r.value for r in allowed_roles]
            raise PermissionDeniedError(
                f"Action requires one of the following roles: {role_names}. Your current role is '{current_user.role.value}'."
            )
        return current_user

    return role_checker


# Type aliases for clean dependency injection in route endpoints
SessionDep = Annotated[AsyncSession, Depends(get_async_db)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
CurrentAdminDep = Annotated[
    User,
    Depends(require_roles([UserRole.ADMIN])),
]
CurrentManagerDep = Annotated[
    User,
    Depends(require_roles([UserRole.ADMIN, UserRole.MANAGER])),
]
