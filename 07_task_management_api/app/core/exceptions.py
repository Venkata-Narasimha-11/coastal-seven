"""Domain-specific exceptions and global exception handlers for Day 7."""

from typing import Any, Dict, List, Optional
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


class DomainException(Exception):
    """Base domain exception with status code and error classification."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "BAD_REQUEST",
        headers: Optional[Dict[str, str]] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.headers = headers
        self.details = details


class EntityNotFoundError(DomainException):
    """Raised when a requested resource is not found."""

    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
        )


class DuplicateEntityError(DomainException):
    """Raised when creating a resource that violates uniqueness constraints."""

    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_name} with {field} '{value}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
            error_code="DUPLICATE_ENTITY",
        )


class AuthenticationError(DomainException):
    """Raised when authentication credentials fail or token is invalid."""

    def __init__(self, message: str = "Could not validate credentials or token expired."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="UNAUTHORIZED",
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(DomainException):
    """Raised when authenticated user lacks permissions for an operation."""

    def __init__(self, message: str = "Operation not permitted. Insufficient privileges."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="PERMISSION_DENIED",
        )


class InvalidWorkflowTransitionError(DomainException):
    """Raised when a task status transition violates the workflow state machine."""

    def __init__(
        self,
        current_status: str,
        target_status: str,
        allowed_transitions: List[str],
        reason: Optional[str] = None,
    ):
        allowed_str = ", ".join(f"'{s}'" for s in allowed_transitions) if allowed_transitions else "None"
        base_msg = f"Cannot transition task from '{current_status}' to '{target_status}'. Allowed transitions: [{allowed_str}]."
        if reason:
            base_msg += f" Reason: {reason}"
        super().__init__(
            message=base_msg,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_STATUS_TRANSITION",
            details={
                "current_status": current_status,
                "target_status": target_status,
                "allowed_transitions": allowed_transitions,
            },
        )


class InvalidOperationError(DomainException):
    """Raised when an operation is logically invalid."""

    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            error_code="INVALID_OPERATION",
            details=details,
        )


# Global Exception Handlers for FastAPI
async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Translates domain exceptions into standardized JSON responses."""
    content: Dict[str, Any] = {
        "success": False,
        "detail": exc.message,
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details,
        },
        "status_code": exc.status_code,
    }
    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Formats Pydantic 422 validation errors uniformly."""
    formatted_errors = []
    for err in exc.errors():
        loc = " -> ".join(str(l) for l in err.get("loc", []))
        formatted_errors.append({
            "field": loc,
            "message": err.get("msg"),
            "type": err.get("type"),
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "detail": "Request validation failed.",
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "One or more fields failed validation.",
                "details": formatted_errors,
            },
            "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Standardizes Starlette/FastAPI HTTPExceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "detail": exc.detail,
            "error": {
                "code": "HTTP_EXCEPTION",
                "message": str(exc.detail),
                "details": None,
            },
            "status_code": exc.status_code,
        },
        headers=exc.headers,
    )
