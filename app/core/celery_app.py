from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "telegram_service",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["app.workers.tasks"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery.conf.beat_schedule = {
    "scan-channels-every-1min": {
        "task": "app.workers.tasks.scan_channels_task",
        "schedule": 60.0,
    },
    "aggregate-message-stats-daily": {
        "task": "app.workers.tasks.aggregate_message_stats_daily",
        "schedule": 86400.0,  # раз в сутки
    },
} 