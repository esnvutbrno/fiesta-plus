from __future__ import annotations

import datetime
import typing
from collections.abc import Reversible
from operator import attrgetter
from pathlib import Path

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


@register.simple_tag
def interpolate_to_list(value: float, *values: typing.Any):
    return values[int(min(1, max(0, value)) * len(values))]


@register.filter
def multiply(first, second):
    return first * second


@register.filter(name="int")
def int_(value):
    return int(value)


@register.filter(name="zip")
def zip_(value, another):
    return zip(value, another, strict=True)
