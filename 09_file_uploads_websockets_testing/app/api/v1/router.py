"""API v1 Router aggregation."""

from fastapi import APIRouter

from app.api.v1.endpoints import integrated, uploads, websockets

api_router = APIRouter()

api_router.include_router(uploads.router)
api_router.include_router(websockets.router)
api_router.include_router(integrated.router)
