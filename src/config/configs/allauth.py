from config.settings import INSTALLED_APPS, MIDDLEWARE
import os


USE_ALLAUTH = os.getenv('USE_ALLAUTH', 'False')
USE_ALLAUTH = USE_ALLAUTH.lower() == 'true'

if USE_ALLAUTH:
    MIDDLEWARE += ["allauth.account.middleware.AccountMiddleware",]

    INSTALLED_APPS += [
        'allauth',
        'allauth.account',
        'allauth.socialaccount',
        'allauth.socialaccount.providers.google',
    ]


    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend',
    ]

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'APP': {
                'client_id': os.getenv('GOOGLE_CLIENT_ID'),
                'secret': os.getenv('GOOGLE_SECRET'),
                'key': ''
            }
        }
    }

    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    SOCIALACCOUNT_QUERY_EMAIL = True
    ACCOUNT_USERNAME_REQUIRED = False
    ACCOUNT_USER_MODEL_USERNAME_FIELD = None
    ACCOUNT_LOGOUT_ON_GET = True
    ACCOUNT_UNIQUE_EMAIL = True
    ACCOUNT_EMAIL_REQUIRED = True
    ACCOUNT_AUTHENTICATION_METHOD = 'email'
    #only one email allowed! but user can change it, set False thehn user can add multiple emails
    ACCOUNT_CHANGE_EMAIL=True
    ACCOUNT_CONFIRM_EMAIL_ON_GET=True
    ACCOUNT_EMAIL_NOTIFICATIONS=True

