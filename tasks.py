from celery import Celery


app = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

@app.task
def my_task(name):
    print(f"Running Tasks, args = {name}")
    return f"Hello! {name}"