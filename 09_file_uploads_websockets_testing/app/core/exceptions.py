"""Custom application exceptions and HTTP exception handlers."""

from typing import Any, Dict, Optional

from fastapi import Request, status
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details or {}


class FileValidationError(AppException):
    """Raised when an uploaded file violates format, extension, or integrity rules."""

    def __init__(
        self,
        message: str = "Invalid file payload or unsupported format.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            details=details,
        )


class FileTooLargeError(AppException):
    """Raised when an uploaded file exceeds the configured size limit."""

    def __init__(
        self,
        message: str = "File size exceeds the permitted limit.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            details=details,
        )


class FileNotFoundAppError(AppException):
    """Raised when a requested stored file cannot be located."""

    def __init__(
        self,
        message: str = "Requested file not found.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details=details,
        )


class WebSocketClientError(AppException):
    """Raised during WebSocket connection or messaging failures."""

    def __init__(
        self,
        message: str = "WebSocket communication error.",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details,
        )


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global handler for AppException subclasses returning standardized JSON."""
    if isinstance(exc, AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "error": exc.__class__.__name__,
                "message": exc.message,
                "details": exc.details,
                "path": request.url.path,
            },
        )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "InternalServerError",
            "message": str(exc),
            "path": request.url.path,
        },
    )
