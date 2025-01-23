import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


AUTH_USER_MODEL = 'user.User'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
SESSION_COOKIE_AGE = 60 * 60 * 24 * 3
LOGOUT_REDIRECT_URL = 'user:username_login'
LOGIN_URL = 'user:username_login'
LOGIN_REDIRECT_URL = 'user:profile'
SITE_ID=1


ALLOWED_HOSTS = []



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django_celery_results',
    'django_mailbox',
    
    'django_celery_beat',

    
    'rest_framework',
    'rest_framework_simplejwt',

    'extensions',
    
    'loggerapp.apps.LoggerappConfig',

    'user.apps.UserConfig',
    'nazer.apps.NazerConfig'
    
]

MIDDLEWARE = [
    
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'
print(os.path.join(BASE_DIR, 'templates'))
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'),],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]



LANGUAGE_CODE = "fa-ir"

TIME_ZONE = 'Asia/Tehran'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

# MEDIA_ROOT = BASE_DIR.parent / 'media'

# STATIC_ROOT = BASE_DIR / 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.getenv('DB_NAME', default="nezarat"),
       'USER': os.getenv('DB_USER', default="nezarat"),
       'PASSWORD': os.getenv('DB_PASS', default="nezarat"),
       'HOST': os.getenv('DB_HOST', default="localhost"),
       'PORT': os.getenv('DB_PORT', default="5432"),
   },
}
REDIS_URL = os.getenv('REDIS', default="redis://localhost:6379")
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', default="redis://localhost:6379")

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.redis.RedisCache',
#         'LOCATION':  REDIS_URL,
#     }
# }


from config.configs.logger import LOGGING
from config.configs.email import *
from config.configs.celery import *


CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
ALLOWED_HOSTS = ['*']
SECURE_SSL_REDIRECT=True

SECRET_KEY = os.getenv('SECRET_KEY', default="django-insecure-1zi)$m0x+b1qkdoufbu8(p0l2u9-v#gc0ik28to=_-)mn8t)y9")


STATIC_VERSION = '1.0.2'

SITE_ID = 1

SMS_API_KEY = os.getenv('SMS_API_KEY')
SMS_LINE_NUMBER = os.getenv('SMS_LINE_NUMBER')
SMS_OTP_URL = os.getenv('SMS_OTP_URL')
SMS_OTP_PATTERN = os.getenv('SMS_OTP_PATTERN')
SMS_CHANGE_PHONE_PATTERN = os.getenv('SMS_CHANGE_PHONE_PATTERN')
SMS_ALARM_PATTERN = os.getenv('SMS_ALARM_PATTERN')


#  ############################### DEBUG MODE ##############################
DEBUG = os.getenv('ALLOWED_HOSTS', 'False').lower() in ["true", "1"]
INTERNAL_IPS=[
    '127.0.0.1',
]
# EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')
CSRF_TRUSTED_ORIGINS = os.getenv('CSRF_TRUSTED_ORIGINS', '').split(',')
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False

