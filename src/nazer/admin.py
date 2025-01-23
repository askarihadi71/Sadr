from django.contrib import admin
from .models import Alarm, Device

admin.site.register(Device)
admin.site.register(Alarm)
