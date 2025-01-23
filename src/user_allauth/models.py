import uuid
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.cache import cache
from django.conf import settings
import pyotp
from pytz import all_timezones
from django.utils.translation import gettext_lazy as _
from user.managers import CustomUserManager
from django.utils import timezone
from datetime import timedelta

import logging

logger = logging.getLogger("db")
    


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), blank=False, null=False, unique=True)
    email_confirmed = models.BooleanField(default=False, verbose_name="ایمیل تایید شده است؟")
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    REQUIRED_FIELDS = ["phone",]
    phone = models.CharField(max_length=64, null=True, blank=True)
    objects = CustomUserManager() 


class OTP(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    secret = models.CharField(max_length=32, default=pyotp.random_base32)
    otp_code = models.CharField(max_length=6)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def verify_otp(self, otp_code, remove_after_verify=False):
        # config of TOTP must be same as generating, valid_window need
        totp = pyotp.TOTP(self.secret, interval=300, digits=4)
        is_valid = self.is_valid(otp_code) and totp.verify(otp_code, valid_window=1)
        if is_valid:
            if remove_after_verify:  
                self.delete()
        return is_valid
    
    def is_valid(self, otp_code):
        now = timezone.now()
        return self.otp_code == otp_code and (now - self.updated_at) < timedelta(minutes=5)

    def generate_otp(self):
        now = timezone.now()
        #update secret and tocken every 7 minutes
        if (now - self.created_at) > timedelta(minutes=7):
            self.secret=pyotp.random_base32()
            self.token=uuid.uuid4()
            self.created_at = timezone.now()
            totp = pyotp.TOTP(self.secret, interval=300, digits=4)
            self.otp_code = totp.now()
            self.save()
            return self.otp_code
        # generate 4 digits totp validate for 5 min
        if (now - self.updated_at) >= timedelta(minutes=5) or (now - self.created_at) <= timedelta(minutes=5):
            totp = pyotp.TOTP(self.secret, interval=300, digits=4)
            self.otp_code = totp.now()
            self.save()
        return self.otp_code
    
    class Meta:
        ordering = ['-created_at'] 


class ChangePhoneOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token1 = models.CharField(max_length=4, null=False, blank=False)
    token2 = models.CharField(max_length=4, null=False, blank=False)
    secret1 = models.CharField(max_length=32, default=pyotp.random_base32)
    secret2 = models.CharField(max_length=32, default=pyotp.random_base32)
    new_phone = models.CharField(max_length=10,null=True,blank=True,verbose_name="شماره همراه", validators=[RegexValidator(regex='^[1-9]{1}[0-9]{9}$', message='این مقدار باید  یک شماره همراه و بدون صفر وارد شود.')])
    created_at = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def verify_tokens(user, token1, token2):
        try:
            changePhoneInstance = ChangePhoneOTP.objects.get(user=user)
        except ChangePhoneOTP.DoesNotExist:
            return False, None
        
        now = timezone.now()
        if now - changePhoneInstance.created_at > timedelta(minutes=5):
            return False, None
        
        totp1 = pyotp.TOTP(changePhoneInstance.secret1, interval=300, digits=4)
        totp2 = pyotp.TOTP(changePhoneInstance.secret2, interval=300, digits=4)
        
        token1_is_valid = totp1.verify(token1, valid_window=1)
        token2_is_valid = totp2.verify(token2, valid_window=1)
        
        if token1_is_valid and token2_is_valid:
            new_phone = changePhoneInstance.new_phone
            user = changePhoneInstance.user
            user.phone = changePhoneInstance.new_phone
            user.save()
            changePhoneInstance.delete()
            return True, new_phone
        
        return False, None


    @staticmethod
    def generate_pair_tokens(user, new_phone):
        changePhoneInstance = ChangePhoneOTP.objects.filter(user=user)
        changePhoneInstance.delete()
        
        secret1 = pyotp.random_base32()
        secret2 = pyotp.random_base32()
        totp1 = pyotp.TOTP(secret1, interval=300, digits=4)
        totp2 = pyotp.TOTP(secret2, interval=300, digits=4)
        token1 = totp1.now()
        token2 = totp2.now()
        
        changePhoneInstance = ChangePhoneOTP(
            user = user,
            secret1=secret1,
            secret2=secret2,
            token1 = token1,
            token2 = token2,
            new_phone=new_phone,
            created_at = timezone.now()
        )
        changePhoneInstance.full_clean()
        changePhoneInstance.save()
        
        return token1, token2
    
    def __str__(self) -> str:
        return f'{self.user.username}'



class AppConfig(models.Model):
    sms_api_key = models.CharField(max_length=256)
    sms_linenumber = models.CharField(max_length=256, null=True, blank=True)
    
    
    class Meta:
        verbose_name = "App Configuration"
        
    @staticmethod
    def _cache_enabled():
        return hasattr(settings, 'CACHES') and 'default' in settings.CACHES
        
    def save(self, *args, **kwargs):
        if AppConfig.objects.exists():
            self.pk = AppConfig.objects.first().pk
        super(AppConfig, self).save(*args, **kwargs)
        if self._cache_enabled():
            try:
                cache.set('app_config', self, 18000)
            except Exception as e:
                logger.error(f"Error saving device config to cache: {e}")
            
    def delete(self, *args, **kwargs):
        pass
        
        def __str__(self):
            return "App Configuration"
        
    