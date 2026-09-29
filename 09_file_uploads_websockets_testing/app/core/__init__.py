"""Core module initialization."""

from app.core.config import settings
from app.core.exceptions import (
    AppException,
    FileNotFoundAppError,
    FileTooLargeError,
    FileValidationError,
    WebSocketClientError,
    app_exception_handler,
)
from app.core.security import (
    detect_mime_from_magic_bytes,
    is_safe_path,
    sanitize_filename,
)

__all__ = [
    "settings",
    "AppException",
    "FileValidationError",
    "FileTooLargeError",
    "FileNotFoundAppError",
    "WebSocketClientError",
    "app_exception_handler",
    "sanitize_filename",
    "detect_mime_from_magic_bytes",
    "is_safe_path",
]
