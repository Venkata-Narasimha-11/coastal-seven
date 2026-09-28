"""Application Launcher Script for Day 5."""

import sys
import uvicorn

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from app.core.config import settings

if __name__ == "__main__":
    print("=" * 70)
    print(f">> Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f">> Environment: {settings.ENVIRONMENT} (Debug: {settings.DEBUG})")
    print(f">> OpenAPI Documentation: http://127.0.0.1:8000/docs")
    print(f">> ReDoc Documentation:   http://127.0.0.1:8000/redoc")
    print("=" * 70)

    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
