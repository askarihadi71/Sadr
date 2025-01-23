from django.urls import path
from .views import *


urlpatterns = [
    path("get-profile/", GetProfileAPIView.as_view(), name="get_profile"),
    path("update-profile/", UpdateProfileAPIView.as_view(), name="update_profile"),
    path('request-otp-email/', RequestEmailOTP.as_view(), name='otp_email_request'),
    
]
