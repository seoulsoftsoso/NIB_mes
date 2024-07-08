from django import template
from urllib.parse import urljoin as urllib_urljoin

register = template.Library()

@register.filter
def urljoin(value, arg):
    return urllib_urljoin(str(value), str(arg))
