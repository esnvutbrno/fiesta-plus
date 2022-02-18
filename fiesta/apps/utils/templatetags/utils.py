import datetime
from operator import attrgetter
from pathlib import Path
from typing import Reversible

from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


@register.filter(is_safe=True)
@stringfilter
def strip_file_extension(name: str) -> str:
    return Path(name).with_suffix("").as_posix()


@register.filter
@stringfilter
def date_from_iso(iso: str) -> datetime.datetime:
    return datetime.datetime.fromisoformat(iso)


@register.filter
def date_from_unix(n: int) -> datetime.datetime:
    return datetime.datetime.fromordinal(n)


@register.filter
def map_attrgetter(iterable: Reversible, attr: str):
    return map(attrgetter(attr), iterable)
