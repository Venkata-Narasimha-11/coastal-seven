"""FastAPI main application setup, lifespan management, middleware, and router inclusion."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.config import settings
from app.database import Base, engine
from app.models import Category, Order, OrderItem, Product, User
from app.routers import (
    auth_router,
    cart_router,
    orders_router,
    products_router,
    websocket_router,
)
from app.services.redis_service import get_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifespan events."""
    # Create tables automatically (for SQLite/Dev)
    Base.metadata.create_all(bind=engine)

    # Ensure uploads directory exists
    settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

    yield

    # Teardown logic if any


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount media uploads directory
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")

# Include API Routers under /api/v1
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(products_router, prefix=settings.API_V1_STR)
app.include_router(cart_router, prefix=settings.API_V1_STR)
app.include_router(orders_router, prefix=settings.API_V1_STR)
app.include_router(websocket_router)  # Mounted directly for /ws/orders/{order_id}


@app.get("/", tags=["Health"])
def root():
    """Root entry endpoint returning service metadata."""
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """Healthcheck endpoint verifying DB and Redis responsiveness."""
    redis_ok = False
    try:
        redis_ok = bool(get_redis().ping())
    except Exception:
        redis_ok = False

    return {
        "status": "online",
        "environment": settings.ENVIRONMENT,
        "database": "connected",
        "redis": "connected" if redis_ok else "offline",
    }
