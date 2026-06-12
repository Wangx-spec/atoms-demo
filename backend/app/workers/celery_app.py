try:
    from celery import Celery
except ImportError:  # Celery is optional in the lightweight MVP skeleton.
    Celery = None


celery_app = Celery("atoms_demo") if Celery else None

if celery_app:
    celery_app.conf.broker_url = "redis://redis:6379/0"
    celery_app.conf.result_backend = "redis://redis:6379/1"
