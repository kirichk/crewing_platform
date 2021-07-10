from __future__ import absolute_import
import os
from django.conf import settings
from celery import Celery
from celery.schedules import crontab


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crewing.settings')
app = Celery('crewing')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'delete_not_relevant_posts': {
        'task': 'web_hiring.tasks.delete_old_files',
        'schedule': crontab(hour='*/24'),
    },
    'search_for_new_posts': {
        'task': 'web_hiring.tasks.find_new_posts',
        'schedule': crontab(minute='*/10'),
    },
}
