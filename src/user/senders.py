from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from config.celery import app
from django.urls import reverse  
from django.utils import timezone
from user.models import OTP, ChangePhoneOTP
import requests

import logging

from extensions.utils import jalali_converter

logger = logging.getLogger("db")

def send_otp(user_otp):
    try:
        SMS_API_KEY = settings.SMS_API_KEY
        SMS_LINE_NUMBER= settings.SMS_LINE_NUMBER
        SMS_OTP_URL = settings.SMS_OTP_URL
        SMS_OTP_PATTERN = settings.SMS_OTP_PATTERN

        user = user_otp.user
        user_phone = f'+98{user.phone}'
        otp_code = user_otp.generate_otp()

        headers = {
            'Authorization': f'Bearer {SMS_API_KEY}',
            'Content-Type': 'application/json',  
        }
        data={
            "from":SMS_LINE_NUMBER,
            "pattern_id":SMS_OTP_PATTERN,
            "params":{"code":otp_code},
            "number":user_phone
        }
        if settings.DEBUG:
            print(data)
            return
        try:
            response = requests.post(SMS_OTP_URL, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                print(f'otp sms sent {response_data}')
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                logger.warning("Response:", response.text)
                logger.warning(response.json())
                logger.warning(headers)

        except Exception as e:
            logger.error(f"Error OTP sms send e: {e}")

    except Exception as e:
        logger.error(f"Error login e: {e}")


@app.task(name="send_otp_email")
def send_otp_email(user_pk):
    user = get_user_model().objects.get(pk=user_pk)
    if user.email_confirmed:
        user_email = user.email
        user_otp, created = OTP.objects.get_or_create(user=user)  
        otp_code = user_otp.generate_otp()
        subject = 'پنل صدر نت' 
        message = f'کد ورود شما : {otp_code}'  
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]  
        send_mail(subject, message, from_email, recipient_list)  
        logger.info(f"otp email sent to {user_email}")
        return f"otp email sent to {user_email}"
    return False


@app.task(name="send_verification_email")
def send_verification_email(user_email, token):  
    verification_link = reverse('user:verify_email', args=[token])  
    full_link = f"https://{Site.objects.get_current().name}{verification_link}"
    
    subject = 'پنل صدر نت' 
    message = f'برای تایید ایمیل روی لینک زیر کلیک کنید: {full_link}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]
     
    send_mail(subject, message, from_email, recipient_list) 
    
    logger.info(f"confirm email link sent to {user_email}")
    return f"confirm email link sent to {user_email}"



@app.task(name="send_verification_change_email")
def send_verification_change_email(user_email, token):  
    verification_link = reverse('user:verify_change_email', args=[token])  
    full_link = f"https://{Site.objects.get_current().name}{verification_link}"
    
    subject = 'پنل صدر نت' 
    message = f'برای تایید ایمیل روی لینک زیر کلیک کنید: {full_link}'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]  
     
    send_mail(subject, message, from_email, recipient_list) 
    logger.info(f"confirm email change link sent to {user_email}")
    return f"confirm email change link sent to {user_email}"


@app.task(name="send_change_email_notif")
def send_change_email_notif(user_email, new_email):  

    subject = 'پنل صدر نت' 
    message = f'در {jalali_converter(timezone.now())} ایمل شما در سامانه به {new_email} تغییر کرد'
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email,]  
    
    send_mail(subject, message, from_email, recipient_list) 
    logger.info(f"email change notif sent to {user_email}")
    return f"email change notif sent to {user_email}"
    
    
@app.task(name="send_phone_change_codes") 
def send_phone_change_codes(user_pk, new_phone):
    try:
        SMS_API_KEY = settings.SMS_API_KEY
        SMS_LINE_NUMBER= settings.SMS_LINE_NUMBER
        SMS_OTP_URL = settings.SMS_OTP_URL
        SMS_CHANGE_PHONE_PATTERN = settings.SMS_CHANGE_PHONE_PATTERN

        user_new_phone = f'+98{new_phone}'
        
        token = ChangePhoneOTP.generate_token(
            user=get_user_model().objects.get(pk=user_pk),
            new_phone=new_phone
        )

        headers = {
            'Authorization': f'Bearer {SMS_API_KEY}',
            'Content-Type': 'application/json',  
        }
        data={
            "from":SMS_LINE_NUMBER,
            "pattern_id":SMS_CHANGE_PHONE_PATTERN,
            "params":{"code":token},
            "number":user_new_phone
        }
        try:
            response = requests.post(SMS_OTP_URL, headers=headers, json=data)
            if response.status_code == 200:
                response_data = response.json()
                print(f'change phone sms sent {response_data}')
            else:
                logger.warning(f"Request failed with status code: {response.status_code}")
                logger.warning("Response:", response.text)
                logger.warning(response.json())

        except Exception as e:
            logger.error(f"Error change phone sms send e: {e}")


    except Exception as e:
        logger.error(f"Error login e: {e}")

