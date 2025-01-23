from django import template  
from django.conf import settings  

register = template.Library()  

@register.simple_tag  
def use_alluth():  
    return getattr(settings, 'USE_ALLAUTH', False)  