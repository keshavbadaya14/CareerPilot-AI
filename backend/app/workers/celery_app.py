from celery import Celery

from app.core.config import settings


celery_app = Celery(

    "careerpilot",

    broker=settings.REDIS_URL,

    include=[
        "app.workers.tasks"
    ]
)


celery_app.conf.update(

    task_serializer="json",

    accept_content=["json"],

    task_ignore_result=True,

    timezone="UTC",

    enable_utc=True,

    broker_connection_retry_on_startup=True,

    worker_prefetch_multiplier=1,

    beat_schedule={

        "periodic-job-ingestion": {

            "task": "careerpilot.ingest_all",

            "schedule": (
                settings.INGESTION_INTERVAL_SECONDS
            ),

            "options": {
                "expires": 3600
            }
        }
    }
)