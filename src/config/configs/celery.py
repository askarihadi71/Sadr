# from decouple import config
# from kombu import Queue, Exchange, binding
from celery.signals import task_failure, task_received
from config.settings import CELERY_BROKER_URL
import logging
logger = logging.getLogger("db")


CELERY_BROKER_URL = CELERY_BROKER_URL

# CELERY_BROKER_URL = 'redis://127.0.0.1:6379/0'  


CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True
# CELERY_TASK_RESULT_EXPIRES = 60
# CELERY_RESULT_EXPIRES = 60



# CELERY_RESULT_BACKEND = 'rpc://'

# CELERY_TIMEZONE = "UTC"

# # CELERY_TASK_SOFT_TIME_LIMIT = 20  # seconds
# # CELERY_TASK_TIME_LIMIT = 30  # seconds
# # CELERY_TASK_MAX_RETRIES = 3

# CELERY_TASK_DEFAULT_QUEUE = 'sajjad_default'
# CELERY_TASK_DEFAULT_EXCHANGE = 'sajjad_default'

# ex1 = Exchange('sajjad_ex1', type='topic', durable=False, auto_delete=True)
# CELERY_TASK_QUEUES = (
#     Queue('sajjad_import_data', routing_key='import_data.tasks.#', exchange=ex1, durable=False, auto_delete=True),
#     Queue('interceptions', routing_key='interceptions.tasks.#', exchange=ex1, durable=False, auto_delete=True),

# )

# CELERY_TASK_ROUTES = {
#     'import_data.tasks.*': {'queue': 'sajjad_import_data'},
#     'interceptions.tasks.*': {'queue': 'interceptions'},
# }


@task_failure.connect
def on_task_failure(task_id, exception, args, traceback, einfo, **kwargs):
    logger.error(
        f'task_failure for task id {task_id}, exception {exception}, args {args}, traceback {traceback}, einfo {einfo}')


# @task_received.connect
# def on_task_received(*args, **kwargs):
#     logger.warning(f'task_received kwargs : {kwargs}')