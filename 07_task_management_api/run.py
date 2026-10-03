"""Server launcher script for Day 7 Mini-Project 2 Task Management API."""

import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    print("=" * 75)
    print(f"🚀 Launching {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"📄 Swagger UI Docs : http://127.0.0.1:8000/docs")
    print(f"📚 ReDoc UI Docs   : http://127.0.0.1:8000/redoc")
    print(f"🔍 OpenAPI JSON    : http://127.0.0.1:8000/openapi.json")
    print(f"🩺 Health Check    : http://127.0.0.1:8000/api/v1/health")
    print("=" * 75)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
