
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandParser
from user.models import AppConfig

class Command(BaseCommand):
    help = "add otp configs"
    
    def add_arguments(self, parser):
        parser.add_argument("otp_pattern",type=str,help="otp_pattern")
        return super().add_arguments(parser)
    
    def handle(self, *args, **kwargs):
        otp_pattern = kwargs.get("otp_pattern")
        conf = AppConfig.objects.first()
        if conf == None:
            conf=AppConfig(otp_pattern=otp_pattern)
            conf.save()
            self.stdout.write(self.style.SUCCESS("OTP Configs saved!"))
        else:
            conf.otp_pattern=otp_pattern
            self.stdout.write(self.style.SUCCESS("OTP Configs updated!"))

            