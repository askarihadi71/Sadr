from celery import shared_task
from django.core.mail import send_mail
import logging

logger = logging.getLogger("db")

@shared_task
def send_async_email(subject, message, from_email, recipient_list):
    try:
        send_mail(subject, message, from_email, recipient_list)
    except Exception as e:
        logger.error(e)
        

