from celery import Celery

from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND


celery_app = Celery(
    "universal_follow_up_engine",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND,
    include=["app.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
)
