from django import template

register = template.Library()

@register.filter(name='object_model')
def object_model(obj):
    return obj.__class__.__name__