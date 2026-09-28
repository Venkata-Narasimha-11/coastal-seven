"""FastAPI Dependencies for Database Sessions, Pagination, JWT Authentication, and RBAC."""

from typing import Annotated, Callable, List, Optional
from fastapi import Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import decode_access_token
from app.crud.crud_user import crud_user
from app.db.session import get_async_db
from app.models.user import User

# HTTPBearer scheme: Swagger UI prompt only requires entering the Bearer JWT token (no username/password form)
bearer_scheme = HTTPBearer(
    scheme_name="BearerAuth",
    description="Enter JWT Bearer token only (no username, password, or client credentials needed).",
    auto_error=False,
)

# Export alias for compatibility
oauth2_scheme = bearer_scheme

# Database Session Dependency
SessionDep = Annotated[AsyncSession, Depends(get_async_db)]


class PaginationParams:
    """Dependency handling standard limit-offset pagination."""

    def __init__(
        self,
        page: int = Query(1, ge=1, description="Page number (1-indexed)"),
        page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    ):
        self.page = page
        self.page_size = page_size
        self.skip = (page - 1) * page_size
        self.limit = page_size


class ProductFilterParams:
    """Dependency handling catalog search and filtering parameters."""

    def __init__(
        self,
        search: Optional[str] = Query(None, min_length=1, max_length=100, description="Search term for title/description/SKU"),
        category: Optional[str] = Query(None, min_length=2, max_length=50, description="Category filter"),
        min_price: Optional[float] = Query(None, ge=0.0, description="Minimum price filter"),
        max_price: Optional[float] = Query(None, ge=0.0, description="Maximum price filter"),
        is_available: Optional[bool] = Query(None, description="Filter by availability status"),
        owner_id: Optional[int] = Query(None, ge=1, description="Filter by owner ID"),
    ):
        self.search = search
        self.category = category
        self.min_price = min_price
        self.max_price = max_price
        self.is_available = is_available
        self.owner_id = owner_id


# ------------------------------------------------------------------------------
# 5. USER AUTHENTICATION DEPENDENCY: get_current_user
# ------------------------------------------------------------------------------
async def get_current_user(
    request: Request,
    session: SessionDep,
    auth: Annotated[Optional[HTTPAuthorizationCredentials], Depends(bearer_scheme)],
) -> User:
    """
    Authenticate request via JWT Bearer token.
    Extracts, decodes, and verifies signature and expiration with python-jose,
    then loads the active User record from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials or token expired.",
        headers={"WWW-Authenticate": "Bearer"},
    )

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
        raise credentials_exception

    payload = decode_access_token(token)
    if not payload:
        raise credentials_exception

    # Enforce that only 'access' tokens can authenticate endpoints
    token_type = payload.get("type")
    if token_type and token_type != "access":
        raise credentials_exception

    user_id_str: Optional[str] = payload.get("sub")
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


# ------------------------------------------------------------------------------
# 6. ROLE-BASED ACCESS CONTROL (RBAC) DEPENDENCIES
# ------------------------------------------------------------------------------
def require_roles(*allowed_roles: str) -> Callable:
    """
    Dependency factory enforcing role-based permissions.
    Permits access if the authenticated user has one of allowed_roles or is superuser.
    Raises HTTP 403 Forbidden otherwise.
    """
    async def role_checker(current_user: CurrentUserDep) -> User:
        user_role = current_user.role.lower() if current_user.role else "user"
        if user_role not in allowed_roles and not current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Requires role: {', '.join(allowed_roles)}.",
            )
        return current_user

    return role_checker


# Specific dependency requiring administrator privileges
get_current_admin_user = require_roles("admin")
CurrentAdminUserDep = Annotated[User, Depends(get_current_admin_user)]
