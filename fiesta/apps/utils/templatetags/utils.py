import datetime

from django import template

register = template.Library()


@register.filter
def date_from_iso(iso: str):
    return datetime.datetime.fromisoformat(iso)
