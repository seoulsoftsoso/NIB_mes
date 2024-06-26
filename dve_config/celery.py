from __future__ import absolute_import, unicode_literals

import os

from datetime import timedelta

from celery import Celery

# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'seoulsoft_mes.settings')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dve_config.settings')

app = Celery('scheduler', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'fetch_sensor_values': {
        'task': 'api.tasks.fetch_sensor_values',
        'schedule': crontab(hour='*', minute=0),
        'args': ()
    }
}

# from api.userexam.scheduler import scheduler_make_assignments