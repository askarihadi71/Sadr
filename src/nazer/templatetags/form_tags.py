# templatetags/form_tags.py
from django import template

register = template.Library()

@register.inclusion_tag('custom_input_field.html')
def custom_input_field(label, name, placeholder, input_type="text", form=None, require=False):
    field_value = form[name].value() if form and name in form.fields else ""
    return {
        'label': label,
        'require': require,
        'name': name,
        'placeholder': placeholder,
        'input_type': input_type,
        'value': field_value,
        'has_value': bool(field_value),
    }


@register.inclusion_tag('custom_switch_field.html')
def custom_switch_field(label, name, form=None, require=False):
    checked = form[name].value() if form and name in form.fields else False
    return {
        'label': label,
        'require': require,
        'name': name,
        'checked': bool(checked),
    }


@register.inclusion_tag('custom_foreignkey_field.html')
def custom_foreignkey_field(label, name, choices, form=None, require=False):
    selected_value = form[name].value() if form and name in form.fields else None
    return {
        'label': label,
        'require': require,
        'name': name,
        'choices': choices,
        'selected_value': selected_value,
    }


@register.inclusion_tag('custom_datetime_picker.html')
def custom_datetime_picker(label, name, placeholder, form=None, require=False):
    value = form[name].value() if form and name in form.fields else ""
    return {
        'label': label,
        'require': require,
        'name': name,
        'placeholder': placeholder,
        'value': value,
    }