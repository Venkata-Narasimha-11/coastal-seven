"""FastAPI Application Entrypoint, Lifespan, and Middleware Configuration for Day 7."""

from contextlib import asynccontextmanager
import logging
from typing import AsyncGenerator
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import (
    DomainException,
    domain_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from app.db.base import Base
from app.db.session import async_engine, check_database_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("TaskManagementAPI")

# OpenAPI Tags metadata for interactive Swagger documentation
openapi_tags = [
    {
        "name": "Authentication",
        "description": "JWT-secured registration, login, token refresh, and user profile management.",
    },
    {
        "name": "Users",
        "description": "User queries, profile management, and role-based permissions.",
    },
    {
        "name": "Projects",
        "description": "CRUD operations, team member enrollment, and project-level task status metrics.",
    },
    {
        "name": "Tasks",
        "description": "Task CRUD, status workflow state transitions, assignments, filtering, and audit history.",
    },
    {
        "name": "System",
        "description": "Application health checks and database connectivity diagnostics.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and graceful shutdown."""
    logger.info("Initializing %s v%s...", settings.PROJECT_NAME, settings.VERSION)

    # 1. Verify database connectivity
    connected = await check_database_connection()
    if connected:
        logger.info(
            "Successfully connected to PostgreSQL at %s:%s/%s",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
        )
    else:
        logger.warning(
            "Database connectivity check failed for %s. Ensure database server is running.",
            settings.async_database_url,
        )

    # 2. Synchronize database schema via SQLAlchemy 2.0 metadata
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schema synchronized successfully.")

    yield

    # 3. Graceful shutdown: dispose connection pool
    logger.info("Disposing database connection engine...")
    await async_engine.dispose()
    logger.info("Application shutdown complete.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=openapi_tags,
    lifespan=lifespan,
)

# CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=600,
    )

# Register Exception Handlers
app.add_exception_handler(DomainException, domain_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Unhandled internal server error handler preventing traceback leakage."""
    logger.exception("Unhandled server exception processing request to %s: %s", request.url.path, exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "detail": "An internal server error occurred.",
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing the request.",
                "details": str(exc) if settings.DEBUG else None,
            },
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
        },
    )


# Register API v1 Router
app.include_router(api_router)


@app.get(
    "/",
    tags=["System"],
    summary="API Root",
    description="Provides service metadata and navigation links.",
)
async def root():
    """Service metadata and documentation entry links."""
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "openapi_url": "/openapi.json",
        "health_check": f"{settings.API_V1_STR}/health",
    }
