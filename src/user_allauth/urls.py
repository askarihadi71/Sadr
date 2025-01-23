from django.urls import path, include, re_path
from django.conf import settings
from .views import *

from django.contrib.auth.views import LogoutView


app_name = 'user'
urlpatterns = [
    path('api/', include('user.rest.urls')),

    path('mgm/login/', UsernameLoginView.as_view(), name='login'),

    path('profile/', Profile.as_view(), name="profile")

]

allauth_urls = [
    path('', Login.as_view(), name='username_login'),
    path('login/', UsernameLoginView.as_view(), name='username_login'),
    path("accounts/login/", UsernameLoginView.as_view(), name="account_login"),
    
    path('otp/', OTPLoginView.as_view(), name='otp_login'),
    
    
    path("accounts/logout/", LogoutView.as_view(), name="account_logout"),
    path("accounts/register/", CustomSignupView.as_view(), name="register"),

    path("accounts/inactive/", InactiveAccountView.as_view(), name="account_inactive"),
    path("accounts/email/", EmailView.as_view(), name="account_email"),

    path("accounts/confirm-email/", EmailVerificationSentView.as_view(), name="account_email_verification_sent"),
   
    re_path(r"^accounts/confirm-email/(?P<key>[-:\w]+)/$",
                EmailConfirmView.as_view(),
                name="account_confirm_email",
            ),
    path("accounts/password/change/", PassChange.as_view(), name="account_change_password"),
    path("accounts/password/change/done/", PassChangeDone.as_view(), name="password_change_done", ),

    path("accounts/password/reset/", PassResetView.as_view(), name="account_reset_password"),
	path("accounts/password/reset/done/", PassResetDone.as_view(), name="account_reset_password_done", ),

    path("accounts/password/set/", PasswordSetView.as_view(), name="account_set_password"),
	path("accounts/password/reset/done/", PassResetDone.as_view(), name="account_set_password_done", ),

    re_path(
        r"^accounts/password/reset/key/(?P<uidb36>[0-9A-Za-z]+)-(?P<key>.+)/$",
        PassResetConfirm.as_view(),
        name="account_reset_password_from_key",
        ),

	path("accounts/password/reset/key/done/", PassResetKeyDone.as_view(), name="account_reset_password_done", ),
]

if settings.USE_ALLAUTH:
    urlpatterns += allauth_urls