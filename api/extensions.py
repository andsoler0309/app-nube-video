from celery import Celery
import os

celery = Celery('tasks', broker=os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/0'))
