from django import template
from django.conf import settings

register = template.Library()

@register.simple_tag
def static_version():
    return getattr(settings, "STATIC_VERSION", "1.0.0")
