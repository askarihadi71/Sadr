import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager as DJUserManager
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import make_password

import pyotp
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.core import signing

import logging

logger = logging.getLogger("db")

class UserManager(DJUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        """
        Create and save a user with the given phone, email, and password.
        """
        if not phone:
            raise ValueError("The given phone must be set")
        user = User(phone=phone,is_active=True, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone, password, **extra_fields)



class User(AbstractUser):
    username = None
    phone = models.CharField(max_length=10,unique=True,null=False,blank=False,verbose_name="شماره همراه", validators=[RegexValidator(regex='^[1-9]{1}[0-9]{9}$', message='این مقدار باید  یک شماره همراه و بدون صفر وارد شود.')])
    email_confirmed = models.BooleanField(default=False, verbose_name="ایمیل تایید شده است؟")
    address = models.TextField(null=True, blank=True)
    USERNAME_FIELD = 'phone'

    objects = UserManager()



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


class EmailConfirmation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=256, null=False, blank=False)
    secret = models.CharField(max_length=32, default=pyotp.random_base32)
    new_email = models.EmailField(null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def verify_token(token,new_email=False, remove_after_verify=True):
        try:
            emailConfirmInstance = EmailConfirmation.objects.get(token=token)
        except EmailConfirmation.DoesNotExist:
            return False, None
        
        now = timezone.now()
        if (now - emailConfirmInstance.created_at) <= timedelta(minutes=15):
            email = signing.loads(token,salt=f'verifEmailLink-{emailConfirmInstance.secret}')
            if new_email:
                user = emailConfirmInstance.user
                user.email = emailConfirmInstance.new_email
                user.email_confirmed=True
                user.save() 
                if remove_after_verify:  
                    emailConfirmInstance.delete()
                return True, email
            else:
                try:
                    user = User.objects.filter(email=email).first()
                except User.DoesNotExist:
                    return False, None
                user.email_confirmed=True
                user.save() 
                if remove_after_verify:  
                    emailConfirmInstance.delete()
                return True, None
        else:
            return False, None
    
    @staticmethod
    def generate_token(user, new_email=None):
        emailConfirmInstance = EmailConfirmation.objects.filter(user=user)
        emailConfirmInstance.delete()

        secret=pyotp.random_base32()
        token = signing.dumps(user.email, salt=f'verifEmailLink-{secret}')
        
        new_email=new_email

        if new_email!= None:
            token = signing.dumps(new_email, salt=f'verifEmailLink-{secret}')

        emailConfirmInstance = EmailConfirmation(
            user = user,
            secret=secret,
            token = token,
            new_email=new_email,
            created_at = timezone.now()
        )
        emailConfirmInstance.full_clean()
        emailConfirmInstance.save()
        return token

    def __str__(self) -> str:
        return f'{self.user.username} -> {self.token}'


class ChangePhoneOTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=4, null=False, blank=False)
    secret = models.CharField(max_length=32, default=pyotp.random_base32)
    new_phone = models.CharField(max_length=10,null=True,blank=True,verbose_name="شماره همراه", validators=[RegexValidator(regex='^[1-9]{1}[0-9]{9}$', message='این مقدار باید  یک شماره همراه و بدون صفر وارد شود.')])
    created_at = models.DateTimeField(blank=True, null=True)

    @staticmethod
    def verify_token(user, token):
        try:
            changePhoneInstance = ChangePhoneOTP.objects.get(user=user)
        except ChangePhoneOTP.DoesNotExist:
            return False, None
        
        now = timezone.now()
        if now - changePhoneInstance.created_at > timedelta(minutes=5):
            return False, None
        
        totp = pyotp.TOTP(changePhoneInstance.secret, interval=300, digits=4)
        
        token1_is_valid = totp.verify(token, valid_window=1)
        
        if token1_is_valid:
            new_phone = changePhoneInstance.new_phone
            user = changePhoneInstance.user
            user.phone = changePhoneInstance.new_phone
            user.save()
            changePhoneInstance.delete()
            return True, new_phone
        
        return False, None


    @staticmethod
    def generate_token(user, new_phone):
        changePhoneInstance = ChangePhoneOTP.objects.filter(user=user)
        changePhoneInstance.delete()
        
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret, interval=300, digits=4)
        token = totp.now()
        
        changePhoneInstance = ChangePhoneOTP(
            user = user,
            secret=secret,
            token = token,
            new_phone=new_phone,
            created_at = timezone.now()
        )
        changePhoneInstance.full_clean()
        changePhoneInstance.save()
        
        return token
    
    def __str__(self) -> str:
        return f'{self.user.username}'


class AppConfig(models.Model):
    sms_linenumber = models.CharField(max_length=256, null=True, blank=True)
    otp_pattern = models.TextField(null=True, blank=True)
    change_phone_pattern = models.CharField(max_length=256, null=True, blank=True)

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
        
        

    
    
    