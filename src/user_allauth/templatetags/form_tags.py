from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_field_with_errors(field, css_class="input border-red-500"):
    css_class = css_class if field.errors else "input"
    field_html = field.as_widget(attrs={"class": css_class})
    
    errors_html = ""
    if field.errors:
        errors_html = '<div class="text-red-500 md:text-sm text-xs">'
        for error in field.errors:
            errors_html += f'<p>{error}</p>'
        errors_html += '</div>'
    
    return mark_safe(f'{field_html}{errors_html}')



