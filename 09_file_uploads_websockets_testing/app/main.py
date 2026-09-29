"""FastAPI main application entrypoint.

Configures static file mounting, exception handlers, WebSocket routes,
and serves the real-time notification dashboard.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints import websockets as ws_endpoints
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppException, app_exception_handler


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager: ensures directories exist on startup."""
    settings.ensure_directories()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-Time Media & Notification Hub: File Uploads, WebSockets, Pillow Image Processing, and Pytest Testing",
    lifespan=lifespan,
)

# Enable CORS for cross-origin WebSocket and HTTP testing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom exception handler
app.add_exception_handler(AppException, app_exception_handler)

# Ensure folders exist before mounting
settings.ensure_directories()

# Mount static file directories:
# 1. Mount uploaded media files (originals & thumbnails) at /static/uploads
app.mount(
    "/static/uploads",
    StaticFiles(directory=str(settings.resolved_upload_dir)),
    name="uploads",
)

# 2. Mount frontend static assets at /static
app.mount(
    "/static",
    StaticFiles(directory=str(settings.resolved_static_dir)),
    name="static",
)

# Include API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)

# Direct root WebSocket routes for convenience
app.add_api_websocket_route("/ws/{client_id}", ws_endpoints.websocket_endpoint)
app.add_api_websocket_route(
    "/ws/channel/{channel_name}/{client_id}",
    ws_endpoints.websocket_channel_endpoint,
)


@app.get("/", summary="Real-time Web Dashboard UI")
def serve_dashboard() -> FileResponse:
    """Serve the real-time file upload & WebSocket notification web application."""
    index_path = settings.resolved_static_dir / "index.html"
    return FileResponse(path=index_path, media_type="text/html")


@app.get("/health", summary="Health check")
def health_check() -> dict:
    """Service health and readiness check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }
