"""Central application configuration using Pydantic Settings V2 for Day 7."""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    # Project metadata
    PROJECT_NAME: str = "Enterprise Task Management REST API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = (
        "Production-grade Task Management API with JWT Auth, RBAC, Status Workflow, "
        "Filtering & Pagination, Alembic Migrations, and Postman Collection."
    )
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database Configuration (PostgreSQL on port 5432)
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5432
    DB_NAME: str = "task_management_api_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_ECHO: bool = False
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Fallback SQLite DB
    USE_SQLITE_FALLBACK: bool = False
    SQLITE_DB_PATH: str = "task_management.db"

    # Security & JWT Token Settings
    SECRET_KEY: str = "day7-super-secret-jwt-access-key-production-ready-min-32-chars-long"
    REFRESH_SECRET_KEY: str = "day7-super-secret-jwt-refresh-key-production-ready-min-32-chars-long"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Initial superuser bootstrap credentials
    FIRST_SUPERUSER_EMAIL: str = "admin@taskmanager.io"
    FIRST_SUPERUSER_PASSWORD: str = "AdminPassword123!"
    FIRST_SUPERUSER_USERNAME: str = "admin"

    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Parse CORS origins if provided as comma-separated string or JSON list."""
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return v

    @property
    def async_database_url(self) -> str:
        """Construct PostgreSQL asyncpg connection URI or SQLite fallback URI."""
        if self.USE_SQLITE_FALLBACK:
            sqlite_path = BASE_DIR / self.SQLITE_DB_PATH
            return f"sqlite+aiosqlite:///{sqlite_path.as_posix()}"

        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+asyncpg://{self.DB_USER}{password_part}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Construct synchronous connection URI for Alembic migrations."""
        if self.USE_SQLITE_FALLBACK:
            sqlite_path = BASE_DIR / self.SQLITE_DB_PATH
            return f"sqlite:///{sqlite_path.as_posix()}"

        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+psycopg2://{self.DB_USER}{password_part}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
