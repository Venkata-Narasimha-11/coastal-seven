"""
Celery Beat Scheduler Runner

Schedules periodic cron jobs (e.g. heartbeat every 60s, cache maintenance at midnight).
Usage:
    celery -A celery_beat.celery_app beat --loglevel=info
or
    python celery_beat.py
"""

import sys
import os

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.celery_app import celery_app

if __name__ == "__main__":
    print("=" * 65)
    print("  ⏰ Starting Celery Beat Periodic Scheduler")
    print("  📋 Scheduled Tasks:")
    for task_name, task_cfg in celery_app.conf.beat_schedule.items():
        print(f"     - {task_name}: {task_cfg['task']} ({task_cfg['schedule']})")
    print("=" * 65)
    
    celery_app.start(["beat", "--loglevel=info"])
