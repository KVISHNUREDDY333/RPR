# Celery worker stub — not active. FastAPI BackgroundTasks handles async jobs.
# Uncomment and configure when scaling beyond single-process:
#
# from celery import Celery
# from backend.app.core.settings import settings
#
# celery_app = Celery("rpr", broker=settings.REDIS_URL, backend=settings.REDIS_URL)
#
# @celery_app.task
# def process_job_task(job_id: str, file_path: str, user_id: str):
#     import asyncio
#     from backend.app.services.pipeline import run_pipeline
#     asyncio.run(run_pipeline(job_id, file_path, user_id))
