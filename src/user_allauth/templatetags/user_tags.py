from django import template
from django.conf import settings
if settings.USE_ALLAUTH:
    from allauth.account.models import EmailAddress

register = template.Library()

@register.simple_tag
def is_email_verified(user):
    if not user.is_authenticated:
        return False
    if settings.USE_ALLAUTH:
        email_address = EmailAddress.objects.filter(user=user, primary=True).first()
    else:
        return False
    return email_address.verified
