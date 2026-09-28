"""Application Domain Exceptions and Global Handlers."""

from typing import Any, Dict, Optional
from fastapi import Request, status
from fastapi.responses import JSONResponse


class DomainException(Exception):
    """Base domain exception with status code and detail mapping."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict[str, str]] = None,
        extra: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.headers = headers
        self.extra = extra or {}


class EntityNotFoundError(DomainException):
    def __init__(self, entity_name: str, identifier: Any):
        super().__init__(
            message=f"{entity_name} with identifier '{identifier}' was not found.",
            status_code=status.HTTP_404_NOT_FOUND,
        )


class DuplicateEntityError(DomainException):
    def __init__(self, entity_name: str, field: str, value: Any):
        super().__init__(
            message=f"{entity_name} with {field} '{value}' already exists.",
            status_code=status.HTTP_409_CONFLICT,
        )


class AuthenticationError(DomainException):
    def __init__(self, message: str = "Could not validate credentials or token expired."):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            headers={"WWW-Authenticate": "Bearer"},
        )


class PermissionDeniedError(DomainException):
    def __init__(self, message: str = "Operation not permitted. Insufficient privileges."):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
        )


class InvalidOperationError(DomainException):
    def __init__(self, message: str):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


async def domain_exception_handler(request: Request, exc: DomainException) -> JSONResponse:
    """FastAPI global exception handler translating domain errors to standardized JSON responses."""
    content: Dict[str, Any] = {
        "detail": exc.message,
        "error_type": exc.__class__.__name__,
    }
    if exc.extra:
        content["context"] = exc.extra

    return JSONResponse(
        status_code=exc.status_code,
        content=content,
        headers=exc.headers,
    )
