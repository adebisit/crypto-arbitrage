from tasks.celery import celery_app
from celery import shared_task

# @celery_app.task
@shared_task
def my_task(name):
    print(f"Running Tasks, args = {name}")
    return f"Hello! {name}"