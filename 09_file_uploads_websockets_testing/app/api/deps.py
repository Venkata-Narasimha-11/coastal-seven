"""API dependencies for dependency injection."""

from app.services.file_service import FileService, file_service
from app.services.image_service import ImageService, image_service
from app.services.websocket_manager import ConnectionManager, manager


def get_connection_manager() -> ConnectionManager:
    """Provide the singleton WebSocket ConnectionManager instance."""
    return manager


def get_file_service() -> FileService:
    """Provide the singleton FileService instance."""
    return file_service


def get_image_service() -> ImageService:
    """Provide the singleton ImageService instance."""
    return image_service
