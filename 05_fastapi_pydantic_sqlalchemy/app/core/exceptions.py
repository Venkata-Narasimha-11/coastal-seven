"""Custom domain exceptions and exception handlers for FastAPI."""

from fastapi import Request, status
from fastapi.responses import JSONResponse


class DomainException(Exception):
    """Base class for all domain-specific errors."""

    def __init__(self, message: str, detail: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.detail = detail


class EntityNotFoundError(DomainException):
    """Raised when a requested resource does not exist in the database."""
    pass


class EntityAlreadyExistsError(DomainException):
    """Raised when an operation would violate unique constraints (e.g. duplicate email/SKU)."""
    pass


class ValidationError(DomainException):
    """Raised when business logic validation fails."""
    pass


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """Handle custom domain exceptions and translate to structured HTTP responses."""
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, EntityNotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, EntityAlreadyExistsError):
        status_code = status.HTTP_409_CONFLICT

    return JSONResponse(
        status_code=status_code,
        content={
            "error": exc.__class__.__name__,
            "message": exc.message,
            "detail": exc.detail or None,
            "path": str(request.url.path),
        },
    )
