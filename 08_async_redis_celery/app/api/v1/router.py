from fastapi import APIRouter

from app.api.v1.endpoints import (
    async_demo,
    cache_demo,
    rate_limit_demo,
    celery_demo,
    comparison_demo,
    integrated,
)

api_router = APIRouter()

api_router.include_router(async_demo.router)
api_router.include_router(cache_demo.router)
api_router.include_router(rate_limit_demo.router)
api_router.include_router(celery_demo.router)
api_router.include_router(comparison_demo.router)
api_router.include_router(integrated.router)
