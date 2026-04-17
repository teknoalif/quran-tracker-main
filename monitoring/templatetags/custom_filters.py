from django import template
register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key) if dictionary else None

@register.filter
def subtract(value, arg):
    try:
        return int(value) - int(arg)
    except (ValueError, TypeError):
        return 0
