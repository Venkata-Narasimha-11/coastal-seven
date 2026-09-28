"""Application Configuration using Pydantic Settings V2 for Day 6."""

from pathlib import Path
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Centralized application settings with environment variable management."""

    # Project metadata
    PROJECT_NAME: str = "FastAPI Authentication & Security API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Production-grade REST API demonstrating passlib bcrypt, python-jose JWT, OAuth2, RBAC, and CORS"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # PostgreSQL Database credentials
    DB_HOST: str = "127.0.0.1"
    DB_PORT: int = 5433
    DB_NAME: str = "fastapi_store_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = ""
    DB_ECHO: bool = False

    # Connection Pool Settings
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_TIMEOUT: int = 30

    # Security & JWT Token Settings (Day 6)
    SECRET_KEY: str = "day6-super-secure-jwt-access-secret-key-change-in-production-min-32-bytes"
    REFRESH_SECRET_KEY: str = "day6-super-secure-jwt-refresh-secret-key-change-in-production-min-32-bytes"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Cross-Origin Resource Sharing (CORS) Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ]

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
        """Construct PostgreSQL asyncpg connection URI for SQLAlchemy 2.0 AsyncEngine."""
        password_part = f":{self.DB_PASSWORD}" if self.DB_PASSWORD else ""
        return (
            f"postgresql+asyncpg://{self.DB_USER}{password_part}@"
            f"{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    @property
    def sync_database_url(self) -> str:
        """Construct PostgreSQL psycopg2 connection URI for synchronous tools like Alembic."""
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
