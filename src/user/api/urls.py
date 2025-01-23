from django.urls import path
from .apis import UsersSearchListAPIView,RequestEmailOTP, AppConfigAPIView

urlpatterns = [
    path('search_users/', UsersSearchListAPIView.as_view(), name='search_users'),
    path('request-otp-email/', RequestEmailOTP.as_view(), name='otp_email_request'),
    path('config/', AppConfigAPIView.as_view(), name='config'),
    
]
