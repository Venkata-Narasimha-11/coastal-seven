"""
Celery Worker Runner

Windows Platform Note:
----------------------
Windows does not support the POSIX fork() system call used by Celery's default 'prefork' pool.
Therefore, on Windows, Celery worker must be launched with:
    celery -A celery_worker.celery_app worker --loglevel=info -P solo
or
    python celery_worker.py
"""

import sys
import os
import platform

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_app import celery_app

if __name__ == "__main__":
    is_windows = platform.system() == "Windows"
    pool_arg = ["-P", "solo"] if is_windows else ["-P", "prefork"]
    
    print("=" * 65)
    print(f"  ⚡ Starting Celery Worker ({'Windows Solo Mode' if is_windows else 'Prefork Pool'})")
    print("  📦 Broker:  ", celery_app.conf.broker_url)
    print("  💾 Backend: ", celery_app.conf.result_backend)
    print("=" * 65)
    
    # Launch worker programmatically
    worker_args = ["worker", "--loglevel=info"] + pool_arg
    celery_app.worker_main(worker_args)
