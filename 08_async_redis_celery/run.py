import uvicorn
import os
import sys

# Ensure current directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("=" * 65)
    print("  🚀 Starting Day 8 FastAPI Application")
    print("  📖 Swagger Documentation: http://127.0.0.1:8000/docs")
    print("  🔍 ReDoc Documentation:   http://127.0.0.1:8000/redoc")
    print("=" * 65)
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
