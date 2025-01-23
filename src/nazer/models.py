import hashlib
import os
from django.db import models
from django.utils import timezone
from django.utils.encoding import filepath_to_uri
from django.utils.text import get_valid_filename
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model
from extensions.utils import jalali_converter


def hashed_upload_path(instance, filename):
    base_directory = 'alarms/'
    salt = timezone.now().__str__()
    filename, extension = os.path.splitext(filename)
    if not extension:
        extension = '.unk'
    basename = get_valid_filename(filename)[:64]
    hashed = hashlib.sha256((salt + basename).encode()).hexdigest()
    filename = f"{hashed}{extension}"

    return filepath_to_uri(os.path.join(base_directory, filename))


class Device(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=150, default="-", null=True)
    email = models.EmailField(null=False, blank=False)
    address = models.TextField(null=True, blank=True)
    description = models.CharField(max_length=250, default="-", null=True)
    
    def __str__(self):
        return f'Device: {self.title}'



class Alarm(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    alarm_type = models.CharField(max_length=250, null=False, blank=False)
    channel = models.IntegerField(default=1, null=True, blank=True)
    time = models.DateTimeField()
    device_name = models.CharField(max_length=250, null=False, blank=False)
    alarm_name = models.CharField(max_length=250, null=False, blank=False)
    ip = models.GenericIPAddressField()
    file = models.FileField(upload_to=hashed_upload_path, null=True,blank=True, validators=[
        FileExtensionValidator(allowed_extensions=['png', 'jpg']),
    ])
    original_file_name = models.TextField(null=True,blank=True)
    is_sms_sent = models.BooleanField(default=False)
    is_email_sent = models.BooleanField(default=False)
    handled = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def jTime(self):
        return jalali_converter(self.time)

    def __str__(self):
        return f'{self.time} - Alarm Name: {self.device_name} - Alarm Name: {self.alarm_name}'
    
    class Meta:
        indexes = [
            models.Index(fields=['time']),
            models.Index(fields=['device_name']),
            models.Index(fields=['alarm_name']),
            models.Index(fields=['alarm_type']),
            models.Index(fields=['ip']),
        ]

class Alarm_SMS(models.Model):
    ...

class Alarm_Email(models.Model):
    ...