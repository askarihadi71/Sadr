from django.contrib.auth.models import BaseUserManager
from django.conf import settings
if settings.USE_ALLAUTH:
    from allauth.account.models import EmailAddress

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        created_user = self.create_user(email, password, **extra_fields)
        
        if settings.USE_ALLAUTH:
            allauth_email = EmailAddress(
                user=created_user,
                email=created_user.email,
                verified=True,
                primary=True
            )
            allauth_email.full_clean()
            allauth_email.save()


        return created_user
