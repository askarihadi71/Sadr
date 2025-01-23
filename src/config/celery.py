import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_incomming_emails':{
        'task': 'nazer.tasks.get_emails',
        'schedule': 10.0
    },
    'process_emails':{
        'task': 'nazer.tasks.process_emails',
        'schedule': 10.0
    },
    'cleanup_emails': {
        'task': 'nazer.tasks.cleanup_emails', 
        'schedule': crontab(hour=5, minute=0),
    },
}

# app.conf.beat_schedule = {
#     'cleanup-celery-results':{
#         'task': 'celery_monitor.tasks.cleanup_celery_results',
#         'schedule':  crontab(minute='*/1')
#     },
# }