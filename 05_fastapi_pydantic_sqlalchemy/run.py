"""Launcher script for FastAPI application using Uvicorn."""

import sys
import uvicorn
from app.core.config import settings

if __name__ == "__main__":
    # Ensure stdout handles UTF-8 on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    print("=" * 70)
    print(f"[*] Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    print(f"[*] Environment: {settings.ENVIRONMENT} | Debug: {settings.DEBUG}")
    print(f"[*] Interactive Swagger Docs: http://127.0.0.1:8000/docs")
    print(f"[*] ReDoc Documentation:      http://127.0.0.1:8000/redoc")
    print(f"[*] API Base Route:           http://127.0.0.1:8000{settings.API_V1_STR}")
    print("=" * 70)

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
