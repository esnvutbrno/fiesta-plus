import datetime
from _operator import attrgetter
from typing import Reversible

from django import template

register = template.Library()


@register.filter
def date_from_iso(iso: str):
    return datetime.datetime.fromisoformat(iso)


@register.filter
def map_attrgetter(iterable: Reversible, attr: str):
    return map(attrgetter(attr), iterable)
