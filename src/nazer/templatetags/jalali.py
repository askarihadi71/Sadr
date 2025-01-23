from extensions.utils import jalali_converter
from django import template
from django.utils.timezone import now


register = template.Library()

@register.filter
def jalali(date):
    if date is None or date == '':
        return '-'
    return jalali_converter(date)

@register.filter
def time_delta(date):
    try:
        """
        Returns a human-readable time delta between the current time and the created time.
        """
        if date is None or date in ['' , '-']:
            return 9999
        delta = now() - date
        
        # Convert the timedelta to seconds
        seconds = int(delta.total_seconds())
        minutes = seconds // 60
        return minutes
    except Exception as e:
        print(e)
    
