from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ChangePhoneOTP, EmailConfirmation, User, OTP, AppConfig
from django.contrib.auth.admin import UserAdmin


UserAdmin.fieldsets[1][1]['fields'] = (
    'phone',
    'email',
    'email_confirmed',
    'address'
)


UserAdmin.fieldsets[2][1]['fields'] = (
    "is_active",
    "is_staff",
    "is_superuser",
)
UserAdmin.fieldsets[0][1]['fields']=( "password",)
UserAdmin.ordering = ("email",)
UserAdmin.list_display = ("pk","email", "first_name", "last_name", "is_staff", 'is_active', 'is_superuser','email_confirmed', 'address')
UserAdmin.search_fields = ("first_name", "last_name", "email")
# UserAdmin.readonly_fields = ['email',]
UserAdmin.list_filter = ("is_staff", "is_superuser", "is_active")

admin.site.register(User, UserAdmin)

class OTPAdmin(admin.ModelAdmin):
    fields = ['user', 'secret', 'otp_code', 'token']
    list_display = ['user', 'secret', 'otp_code', 'token', 'created_at', 'updated_at']
admin.site.register(OTP, OTPAdmin)


class AppConfigAdmin(admin.ModelAdmin):
    list_display = ['sms_linenumber', 'otp_pattern', 'change_phone_pattern']
    fields = ['sms_linenumber', 'otp_pattern', 'change_phone_pattern']
admin.site.register(AppConfig, AppConfigAdmin)


class EmailConfirmationAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'new_email']
    fields= ['user', 'token', 'created_at', 'new_email']
admin.site.register(EmailConfirmation, EmailConfirmationAdmin)


class ChangePhoneOTPAdmin(admin.ModelAdmin):
    list_display = ['user','token','secret', 'new_phone','created_at']
    fields= ['user','token1', 'secret','new_phone']
admin.site.register(ChangePhoneOTP, ChangePhoneOTPAdmin)


