from __future__ import absolute_import
from celery import Celery
from tasks import *

from celery.schedules import crontab

# Celery Configuration Options


app = Celery('oracle')


app.conf.update(
    timezone="Asia/Krasnoyarsk",
    task_track_started=True,
    task_time_limit=30 * 60,
    broker_url='amqp://guest:guest@rebbitmq:5672//',
)


app.conf.beat_schedule = {
    'creating-new-objects': {
        'task': 'tasks.get_post_from_vk',
        'schedule': crontab(minute=30, hour=23),
    }
}
