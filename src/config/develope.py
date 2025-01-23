from config.settings import *


MIDDLEWARE=['debug_toolbar.middleware.DebugToolbarMiddleware',]+MIDDLEWARE
INSTALLED_APPS=['debug_toolbar',]+INSTALLED_APPS

INTERNAL_IPS=[
    '127.0.0.1',
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

ALLOWED_HOSTS = []
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_SECURE=True
SECURE_SSL_REDIRECT=False