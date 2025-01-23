import os
from django.core.files import File
from django.utils import timezone
from django.conf import settings
from config.celery import app
from celery import shared_task
from django.core.mail import send_mail, EmailMessage
from django_mailbox.models import Mailbox,Message, MessageAttachment
import json
import re
from datetime import datetime
from nazer.models import Alarm, Device
import logging
import requests


logger = logging.getLogger("db")

@shared_task
def get_emails():
    mailboxes = Mailbox.objects.all()
    for mailbox in mailboxes:
        print(f'Getting new mails from {mailbox.name}...')
        messages=mailbox.get_new_mail()
        for message in messages:
                # Process each message as needed
                print(f"Subject: {message.subject}, From: {message.from_header}")


def extract_email(text):
    pattern = r'[\w\.-]+@[\w\.-]+'
    emails = re.findall(pattern, text)
    return emails[0] if emails else None

def parse_email(text):
    # Regular expressions to extract required fields
    try:
        alarm_event_regex = r"Alarm Event:\s*(.+)"
        
        alarm_channel_regex = r"Alarm Input Channel:\s*(.+)"
        alarm_time_regex = r"Alarm Start Time\(D/M/Y H:M:S\):\s*(.+)"
        alarm_stop_time_regex = r"Alarm Stop Time\(D/M/Y H:M:S\):\s*(.+)"

        device_name_regex = r"Alarm Device Name:\s*(.+)"
        alarm_name_regex = r"Alarm Name:\s*(.+)"
        ip_address_regex = r"IP Address:\s*(.+)"


        time_re_search =  re.search(alarm_time_regex, text) if re.search(alarm_time_regex, text) != None else re.search(alarm_stop_time_regex, text)
        alarm_event = re.search(alarm_event_regex, text).group(1)
        alarm_event = re.search(alarm_event_regex, text).group(1)
        alarm_input_channel = re.search(alarm_channel_regex, text).group(1)
        alarm_start_time = time_re_search.group(1)
        alarm_device_name = re.search(device_name_regex, text).group(1)
        alarm_name = re.search(alarm_name_regex, text).group(1)
        ip_address = re.search(ip_address_regex, text).group(1)

        data={
            "alarm_event": alarm_event,
            "alarm_input_channel": alarm_input_channel,
            "alarm_start_time": alarm_start_time,
            "alarm_device_name": alarm_device_name,
            "alarm_name": alarm_name,
            "ip_address": ip_address,
        }
        return data

       
    except Exception as e:
        return None


def send_alarm_email(alarm):
    try:
        device_owner = alarm.device.user
        if not device_owner:
            logger.warning(f"device owner not defined! {alarm.device}")
            return
        body = f"""
            <html>
                <body>
                    <p><strong>Alarm Type:</strong> {alarm.alarm_type}</p>
                    <p><strong>Device Name:</strong> {alarm.device_name}</p>
                    <p><strong>Date and Time:</strong> {alarm.jTime()}</p>
                </body>
            </html>
        """
        email = EmailMessage(
            f"پنل صدر نت - هشدار {alarm.alarm_type}",
            body,
            settings.EMAIL_HOST_USER, 
            [alarm.device.user.email]  # To email
        )
        email.content_subtype = 'html'
        if alarm.file:
            email.attach_file(alarm.file.path)
        email.send()
        alarm.is_email_sent=True
        alarm.save()
        logger.info("Alarm Email sent.")
    except Exception as e:
        logger.error(f"Error sending alarm email: {e}")


def send_alarm_sms(alarm):
    try:
        SMS_API_KEY = settings.SMS_API_KEY
        SMS_LINE_NUMBER= settings.SMS_LINE_NUMBER
        SMS_OTP_URL = settings.SMS_OTP_URL
        SMS_ALARM_PATTERN = settings.SMS_ALARM_PATTERN

        user = alarm.device.user
        if not user:
            logger.warning(f"device owner not defined! {alarm.device}")
            return

        user_phone = f'+98{user.phone}'

        headers = {
            'Authorization': f'Bearer {SMS_API_KEY}',
            'Content-Type': 'application/json',  
        }
        params = {
            "alarm_type":alarm.alarm_type,
            "device":alarm.device_name,
            "time":alarm.jTime()

        }
        data={
            "from":SMS_LINE_NUMBER,
            "pattern_id":SMS_ALARM_PATTERN,
            "params":params,
            "number":user_phone
        }
       
        try:
            response = requests.post(SMS_OTP_URL, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                alarm.is_sms_sent=True
                alarm.save()
                logger.info(f'Alarm sms sent {response_data}')
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                logger.warning("Response:", response.text)
                logger.warning(response.json())
                logger.warning(headers)

        except Exception as e:
            logger.error(f"Error Alarm sms send e: {e}")

    except Exception as e:
        logger.error(f"Error Alarm sms send e: {e}")

@shared_task
def process_emails():
    emails = Message.objects.filter(read__isnull=True)
    for mail in emails:
        mail.read = timezone.now()
        mail.save()
        email_address = extract_email(mail.from_header)
        email_content = parse_email(mail.text)
        if email_content != None:
            Etype=email_content['alarm_event'].lower()
            if Etype == 'intrusion':
                Etype='نفوذ به محل'
            elif Etype == 'tripwire':
                Etype='عبور از خط'
            elif Etype == 'intrusion end':
                Etype='پایان نفوذ به محل'
            elif Etype == 'tripwire':
                Etype='پایان عبور از خط'
            
            try:
                device = Device.objects.get(email=email_address)
            except Device.DoesNotExist:
                logger.warning(f"not defined device email received. {email_content}")
                return
    
            alarm = Alarm(
                device=device,
                alarm_type=Etype,
                channel=email_content['alarm_input_channel'],
                time=timezone.make_aware(datetime.strptime(email_content['alarm_start_time'], '%d/%m/%Y %H:%M:%S')),
                device_name=email_content['alarm_device_name'],
                alarm_name=email_content['alarm_name'],
                ip=email_content['ip_address']
            )
            alarm.full_clean()
            alarm.save()
            if mail.attachments.exists():
                attached_file = mail.attachments.first()
                try:
                    with attached_file.document.open('rb') as f:
                        alarm.file.save(attached_file.get_filename(), File(f), save=True)
                        alarm.original_file_name=attached_file.get_filename()
                        alarm.full_clean()
                        alarm.save()
                except Exception as e:
                    logger.error("error saving email attachment to alarm, alarm:{alarm.pk}, emial:{mail.pk}")

            send_alarm_email(alarm)
            send_alarm_sms(alarm)


from datetime import timedelta

@shared_task
def cleanup_emails():
    days_ago = timezone.now() - timedelta(days=10)
    emails = Message.objects.filter(processed__lt=days_ago)
    emails.delete()