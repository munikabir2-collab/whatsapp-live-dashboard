from celery import Celery

celery = Celery(
    "worker",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery.task
def send_message_task(message: str):
    print("Processing message:", message)