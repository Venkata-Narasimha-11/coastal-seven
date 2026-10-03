"""API v1 router aggregator registering auth, users, projects, and tasks."""

from datetime import datetime, timezone
from fastapi import APIRouter

from app.api.v1.endpoints import auth, projects, tasks, users
from app.core.config import settings
from app.db.session import check_database_connection
from app.schemas.common import HealthCheckResponse

api_router = APIRouter(prefix=settings.API_V1_STR)

# Register endpoint modules
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(projects.router)
api_router.include_router(tasks.router)


@api_router.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["System"],
    summary="Service Health Check",
    description="Validates API server status and live database connectivity.",
)
async def health_check() -> HealthCheckResponse:
    """System health check endpoint."""
    db_connected = await check_database_connection()
    return HealthCheckResponse(
        status="healthy" if db_connected else "degraded",
        database=db_connected,
        version=settings.VERSION,
        timestamp=datetime.now(timezone.utc),
    )
