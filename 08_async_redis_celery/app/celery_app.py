import os
from celery import Celery
from celery.schedules import crontab
from app.core.config import settings

# Initialize Celery Application
celery_app = Celery(
    "day8_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=["app.tasks.celery_tasks"],
)

# Celery Configuration Dictionary
celery_app.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    
    # Task Execution Guarantees
    task_track_started=True,
    task_acks_late=True,               # Acknowledge task only AFTER execution finishes (fault-tolerant)
    worker_prefetch_multiplier=1,      # Fair distribution across workers
    task_time_limit=300,              # Hard timeout in seconds
    task_soft_time_limit=240,         # Soft timeout throwing SoftTimeLimitExceeded
    
    # Eager Mode for local tests / without broker
    task_always_eager=settings.CELERY_TASK_ALWAYS_EAGER,
    task_eager_propagates=True,

    # Celery Beat Periodic Schedule
    beat_schedule={
        "heartbeat-every-60s": {
            "task": "app.tasks.celery_tasks.periodic_heartbeat_task",
            "schedule": 60.0,
            "args": (),
        },
        "cleanup-cache-every-midnight": {
            "task": "app.tasks.celery_tasks.periodic_cleanup_cache_task",
            "schedule": crontab(hour=0, minute=0),
            "args": (),
        },
    },
)

# Optional flower and monitoring settings
celery_app.conf.worker_send_task_events = True
