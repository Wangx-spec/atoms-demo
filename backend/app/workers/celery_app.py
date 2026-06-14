from app.core.config import settings

try:
    from celery import Celery
except ImportError:  # Celery optional; API still imports this module safely.
    Celery = None


if Celery:
    celery_app = Celery(
        "atoms_demo",
        broker=settings.celery_broker_url,
        backend=settings.celery_result_backend,
        include=["app.workers.tasks"],
    )
    celery_app.conf.task_track_started = True
    celery_app.conf.task_serializer = "json"
    celery_app.conf.result_serializer = "json"
    celery_app.conf.accept_content = ["json"]
else:  # pragma: no cover
    celery_app = None
