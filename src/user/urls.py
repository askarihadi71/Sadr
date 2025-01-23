from django.urls import path, include
from .views import *

app_name = 'user'
urlpatterns = [
    path('admin/', UserPassLogin.as_view(), name='username_login'),


    path('', UsernameLoginView.as_view(), name='username_login'),
    path('login/', UsernameLoginView.as_view(), name='username_login'),
    path('otp/', OTPLoginView.as_view(), name='otp_login'),

    path("logout/", UserLogout, name="logout"),
    path('profile', Profile.as_view(), name="profile"),

    path('users', UsersList.as_view(), name="users_list"),
    path('users/create', CreateUser.as_view(), name="create_user"),
    path('users/delete/<int:pk>', DeleteUser.as_view(), name="user_delete"),
    path('users/update/<int:pk>', UserEdit.as_view(), name="user_edit"),
	path('users/resetpass/<int:pk>', set_pass, name="user_reset_pass"),
    

    path('verify-email/', SendVerifyEmailLink.as_view(), name='send_verify_email'),
    path('verify-email/<str:token>/', VerifyEmailView.as_view(), name='verify_email'),
    path('change-email/', ChangeEmailView.as_view(), name='change_email'),
    path('verify-change-email/<str:token>/', VerifyChangeEmailView.as_view(), name='verify_change_email'),
    
    path('change-phone/', ChangePhoneRequestView.as_view(), name='change_phone'),
    path('change-phone-submit/', ChangePhoneView.as_view(), name='change_phone_submit'),
    
    path('api/', include('user.api.urls')),
]
