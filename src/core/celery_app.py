import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery = Celery(
    "telegram_service",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["src.ai_task.tasks"]
)

celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


celery.conf.beat_schedule = {
    "scan-telegram-every-1min": {
        "task": "src.ai_task.tasks.scan_channels_task",
        "schedule": 150.0,
    },
    "aggregate-user-stats-daily": {
        "task": "src.ai_task.tasks.aggregate_user_stats_daily",
        "schedule": 86400.0,  # раз в сутки
    },
}
