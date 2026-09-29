"""Application configuration module using pydantic-settings.

Manages environment variables, storage paths, file limits, and WebSocket settings.
"""

from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

# Root directory of the Day 9 module
MODULE_ROOT: Path = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Central configuration class for the application."""

    PROJECT_NAME: str = "Real-Time Media & Notification Hub"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Base workspace & storage paths (defaults resolve relative to module root)
    UPLOAD_DIR: Path = MODULE_ROOT / "app" / "uploads"
    STATIC_DIR: Path = MODULE_ROOT / "app" / "static"

    # Upload constraints & validation
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_IMAGE_TYPES: List[str] = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/gif",
    ]
    ALLOWED_EXTENSIONS: List[str] = [".jpg", ".jpeg", ".png", ".webp", ".gif"]

    # Image processing specifications
    THUMBNAIL_MAX_WIDTH: int = 150
    THUMBNAIL_MAX_HEIGHT: int = 150
    MEDIUM_MAX_WIDTH: int = 600
    MEDIUM_MAX_HEIGHT: int = 600
    DEFAULT_OUTPUT_FORMAT: str = "WEBP"
    IMAGE_QUALITY: int = 85

    # WebSocket settings
    WS_HEARTBEAT_INTERVAL_SECONDS: int = 30

    @property
    def max_upload_size_bytes(self) -> int:
        """Return maximum upload size in bytes."""
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    @property
    def originals_dir(self) -> Path:
        """Directory for stored original uploaded files."""
        orig = self.UPLOAD_DIR / "originals"
        if not orig.is_absolute():
            orig = MODULE_ROOT / orig
        return orig

    @property
    def thumbnails_dir(self) -> Path:
        """Directory for generated thumbnail images."""
        thumb = self.UPLOAD_DIR / "thumbnails"
        if not thumb.is_absolute():
            thumb = MODULE_ROOT / thumb
        return thumb

    @property
    def resolved_upload_dir(self) -> Path:
        """Ensure absolute upload directory path."""
        if not self.UPLOAD_DIR.is_absolute():
            return MODULE_ROOT / self.UPLOAD_DIR
        return self.UPLOAD_DIR

    @property
    def resolved_static_dir(self) -> Path:
        """Ensure absolute static directory path."""
        if not self.STATIC_DIR.is_absolute():
            return MODULE_ROOT / self.STATIC_DIR
        return self.STATIC_DIR

    def ensure_directories(self) -> None:
        """Ensure all required runtime directories exist."""
        self.resolved_upload_dir.mkdir(parents=True, exist_ok=True)
        self.originals_dir.mkdir(parents=True, exist_ok=True)
        self.thumbnails_dir.mkdir(parents=True, exist_ok=True)
        self.resolved_static_dir.mkdir(parents=True, exist_ok=True)

    model_config = SettingsConfigDict(
        env_file=str(MODULE_ROOT / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
settings.ensure_directories()
