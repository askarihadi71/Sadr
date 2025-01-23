from django.conf import settings
from django.core.mail import send_mail  
from django.http import HttpResponse  
from django.contrib.auth import get_user_model
from config.celery import app
from ippanel import Client
# from ippanel import HTTPError, Error, ResponseCode
from django.urls import reverse  
from django.utils import timezone
from user.models import AppConfig, OTP, ChangePhoneOTP
# from devices_api.celery import app
import logging

from extensions.utils import jalali_converter

logger = logging.getLogger("db")

# @app.task(name="send_otp_sms")
def send_otp(user_otp):
    # user = get_user_model().objects.get(pk=user_pk)
    # user_otp, created = OTP.objects.get_or_create(user=user)  
    try:
        conf = AppConfig.objects.first()

        user = user_otp.user
        user_phone = f'+98{user.phone}'
        otp_code = user_otp.generate_otp()
        sms = Client(conf.sms_api_key)
        pattern = conf.sms_pattern
        linenumber = conf.sms_linenumber
        try:
            pattern_values = {
            "code": otp_code,
            }
            if settings.DEBUG:
                print(f'--------------OTP ------> {otp_code}')
            else:
                message_id = sms.send_pattern(
                    pattern,
                    linenumber,
                    user_phone,
                    pattern_values,
                )
                logger.info(f'otp sms sent {message_id}')
                return f'otp sms sent {message_id}'
        except Error as e: # ippanel sms error
            logger.error(f"Error handled => code: {e.code}, message: {e.message}")
            if e.code == ResponseCode.ErrUnprocessableEntity.value:
                for field in e.message:
                    logger.error(f"Field: {field} , Errors: {e.message[field]}")
        except HTTPError as e: # http error like network error, not found, ...
            logger.error(f"Error handled => code: {e}")

    except Exception as e:
        logger.error(f"Error login e: {e}")


@app.task(name="send_otp_email")
def send_otp_email(user_pk):
    user = get_user_model().objects.get(pk=user_pk)
    if user.email_confirmed:
        user_email = user.email
        user_otp, created = OTP.objects.get_or_create(user=user)  
        otp_code = user_otp.generate_otp()
        subject = 'سامانه مانیتورینگ اکسان'  
        message = f'کد ورود شما : {otp_code}'  
        from_email = 'oxan.bgl@gmail.com'  
        recipient_list = [user_email]  
        send_mail(subject, message, from_email, recipient_list)  
        logger.info(f"otp email sent to {user_email}")
        return f"otp email sent to {user_email}"
    return False


@app.task(name="send_verification_email")
def send_verification_email(user_email, token):  
    verification_link = reverse('account:verify_email', args=[token])  
    full_link = f"https://oxan.bgl.ir{verification_link}"
    
    subject = 'سامانه مانیتورینگ اکسان' 
    message = f'برای تایید ایمیل روی لینک زیر کلیک کنید: {full_link}'
    from_email = 'oxan.bgl@gmail.com'
    recipient_list = [user_email,]
     
    send_mail(subject, message, from_email, recipient_list) 
    
    logger.info(f"confirm email link sent to {user_email}")
    return f"confirm email link sent to {user_email}"



@app.task(name="send_verification_change_email")
def send_verification_change_email(user_email, token):  
    verification_link = reverse('account:verify_change_email', args=[token])  
    full_link = f"https://oxan.bgl.ir{verification_link}"
    
    subject = 'سامانه مانیتورینگ اکسان' 
    message = f'برای تایید ایمیل روی لینک زیر کلیک کنید: {full_link}'
    from_email = 'oxan.bgl@gmail.com'
    recipient_list = [user_email,]  
     
    send_mail(subject, message, from_email, recipient_list) 
    logger.info(f"confirm email change link sent to {user_email}")
    return f"confirm email change link sent to {user_email}"


@app.task(name="send_change_email_notif")
def send_change_email_notif(user_email, new_email):  

    subject = 'سامانه مانیتورینگ اکسان'  
    message = f'در {jalali_converter(timezone.now())} ایمل شما در سامانه به {new_email} تغییر کرد'
    from_email = 'oxan.bgl@gmail.com'  
    recipient_list = [user_email,]  
    
    send_mail(subject, message, from_email, recipient_list) 
    logger.info(f"email change notif sent to {user_email}")
    return f"email change notif sent to {user_email}"
    
    
@app.task(name="send_phone_change_codes") 
def send_phone_change_codes(user_pk, user_old_phone, new_phone):
    try:
        conf = AppConfig.objects.first()
        user_old_phone = f'+98{user_old_phone}'
        user_new_phone = f'+98{new_phone}'
        sms = Client(conf.sms_api_key)
        pattern = conf.change_phone_pattern
        linenumber = conf.sms_linenumber
        
        token1, token2 = ChangePhoneOTP.generate_pair_tokens(user=get_user_model().objects.get(pk=user_pk), new_phone=new_phone)
        
        try:
            pattern_values1 = {
                "code": token1,
            }
            pattern_values2 = {
                "code": token2,
            }
            if settings.DEBUG:
                print(f'--------------SMS To Old Phone {user_old_phone} ------> {token1}')
                print(f'--------------SMS To New Phone {user_new_phone} ------> {token2}')
                logMsg = {
                    'title':'change phone code sent',
                    'old_phone':{user_old_phone},
                    'new_phone':{user_new_phone}
                }
                logger.info(f"{logMsg}")
            else:
                old_phone_msg_id = sms.send_pattern(
                    pattern,
                    linenumber,
                    user_old_phone,
                    pattern_values1,
                )
                new_phone_msg_id = sms.send_pattern(
                    pattern,
                    linenumber,
                    user_new_phone,
                    pattern_values2,
                )
                logger_msg={
                    'title':'change phone code sent',
                    'old_phone':{user_old_phone},
                    'new_phone':{user_new_phone},
                    'old_phone_msg_id':{old_phone_msg_id},
                    'new_phone_msg_id':{new_phone_msg_id}
                    }
                logger.info(f"{logger_msg}")
                return f"{logger_msg}"
        except Error as e: # ippanel sms error
            logger.error(f"Error handled => code: {e.code}, message: {e.message}")
            if e.code == ResponseCode.ErrUnprocessableEntity.value:
                for field in e.message:
                    logger.error(f"Field: {field} , Errors: {e.message[field]}")
        except HTTPError as e: # http error like network error, not found, ...
            logger.error(f"Error handled => code: {e}")

    except Exception as e:
        logger.error(f"Error login e: {e}")

