import os

from celery import Celery
from tasks import *
# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')

# Celery Configuration Options


app = Celery('oracle')


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.

app.conf.update(
    timezone="Asia/Krasnoyarsk",
    task_track_started=True,
    task_time_limit=30 * 60,
    broker_url='amqp://guest:guest@rebbitmq:5672//',
)
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'creating-new-objects': {
        'task': 'tasks.get_post_from_vk',
        'schedule': crontab(minute=18, hour=15)
    }
}
