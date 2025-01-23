from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


UserAdmin.fieldsets[1][1]['fields'] = (
    "first_name",
    "last_name",
    "email",
    "phone"
)


UserAdmin.fieldsets[2][1]['fields'] = (
    "is_active",
    "is_staff",
    "is_superuser",
)
UserAdmin.fieldsets[0][1]['fields']=( "password",)
UserAdmin.ordering = ("email",)
UserAdmin.list_display = ("email", "first_name", "last_name", "is_staff", 'is_active', 'is_superuser')
UserAdmin.search_fields = ("first_name", "last_name", "email", "phone")
UserAdmin.readonly_fields = ['email',]
UserAdmin.list_filter = ("is_staff", "is_superuser", "is_active")

admin.site.register(User, UserAdmin)