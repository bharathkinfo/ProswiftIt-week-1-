from app.celery_app import celery_app


@celery_app.task(name="app.tasks.add_numbers")
def add_numbers(a: int, b: int) -> int:
    """Small Week 1 task used to prove Redis and Celery communication."""
    return a + b
