# atena_participation/celery.py
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'atena_participation.settings')

app = Celery('atena_participation')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
