# celery.py

import os
from celery import Celery
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'syncMate.settings')

app = Celery('syncMate')

# Use the settings from Django's settings.py
app.config_from_object('django.conf:settings', namespace='CELERY')
# Load tasks from all registered apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
