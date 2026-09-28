"""FastAPI Application Entrypoint and Lifecycle Configuration."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import DomainException, domain_exception_handler
from app.db.base import Base
from app.db.session import async_engine, check_database_connection
from app.schemas.common import HealthCheckResponse

# Configure structured logging
logging.basicConfig(
    level=logging.INFO if not settings.DEBUG else logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("FastAPIStore")

# Swagger / OpenAPI documentation metadata tags
tags_metadata = [
    {
        "name": "Users",
        "description": "User account registration, profile management, and catalog ownership.",
        "externalDocs": {
            "description": "User CRUD Specification",
            "url": "https://fastapi.tiangolo.com/tutorial/sql-databases/",
        },
    },
    {
        "name": "Products",
        "description": "Product catalog CRUD operations, multi-attribute filtering, full-text search, and inventory management.",
    },
    {
        "name": "System",
        "description": "Application health checks and database connectivity diagnostics.",
    },
]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager handling application startup and shutdown events."""
    logger.info("Starting up FastAPI application: %s v%s", settings.PROJECT_NAME, settings.VERSION)
    
    # Verify PostgreSQL connectivity on startup
    connected = await check_database_connection()
    if connected:
        logger.info("Successfully connected to PostgreSQL at %s:%s/%s", settings.DB_HOST, settings.DB_PORT, settings.DB_NAME)
    else:
        logger.warning(
            "Could not connect to PostgreSQL on %s:%s/%s. Ensure service is active or migrations are run.",
            settings.DB_HOST,
            settings.DB_PORT,
            settings.DB_NAME,
        )

    # Automatically create tables if not running via alembic (development safeguard)
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified/created via SQLAlchemy 2.0 Base.metadata")

    yield

    # Clean up engine pool on shutdown
    logger.info("Shutting down FastAPI application and disposing connection pools...")
    await async_engine.dispose()
    logger.info("Database connection pools disposed.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)

# Register CORS Middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Register Global Exception Handlers
app.add_exception_handler(DomainException, domain_exception_handler)

# Register API Sub-Routers
app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get(
    "/",
    tags=["System"],
    summary="API Root Information",
    description="Provides quick welcome information and navigation links to Swagger and ReDoc documentation.",
)
async def root() -> dict:
    """Application root endpoint."""
    return {
        "title": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "api_v1_prefix": settings.API_V1_STR,
        "health_check": "/health",
        "message": "Welcome to Day 5: FastAPI, Pydantic V2 & SQLAlchemy 2.0 API!",
    }


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Health Check Probe",
    description="Checks the operational status of the service and active PostgreSQL connectivity.",
)
async def health_check() -> HealthCheckResponse:
    """Diagnostic health check verifying PostgreSQL database connection."""
    db_connected = await check_database_connection()
    status_text = "healthy" if db_connected else "degraded"
    db_status = "connected" if db_connected else "disconnected"

    return HealthCheckResponse(
        status=status_text,
        database=db_status,
        version=settings.VERSION,
    )
