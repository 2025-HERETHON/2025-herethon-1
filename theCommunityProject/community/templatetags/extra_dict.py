from django import template

register = template.Library()

@register.filter
def dict_get(d, key):
    return d.get(int(key))

@register.filter
def dict_get1(d, key):
    if isinstance(d, dict):
        return d.get(key)
    return None

