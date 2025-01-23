from django import template
from urllib.parse import urlencode

register = template.Library()

@register.filter
def remove_page_param(querystring):
    params = querystring.split("&")
    filterd_params = [param for param in params if not param.startswith("page=")]
    return '&'.join(filterd_params)