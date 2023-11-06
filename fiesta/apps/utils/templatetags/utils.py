from __future__ import annotations

import datetime
import hashlib
import typing
from collections.abc import Reversible
from operator import attrgetter
from pathlib import Path

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.timesince import timeuntil

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
    return values[int(min(1, max(0, value)) * len(values)) - 1]


@register.filter
def multiply(first, second):
    return first * second


@register.filter(name="int")
def int_(value):
    return int(value)


@register.filter(name="zip")
def zip_(value, another):
    return zip(value, another, strict=True)


@register.filter
def single_unit_timeuntil(v):
    return timeuntil(v, depth=1)


@register.filter
def get_color_by_text(name: typing.Any) -> str:
    hash_object = hashlib.md5(str(name).encode(), usedforsecurity=False)
    hash_hex = hash_object.hexdigest()

    r = int(hash_hex[0:2], 16)
    g = int(hash_hex[2:4], 16)
    b = int(hash_hex[4:6], 16)

    if r + g + b < 100:
        r += 30
        g += 30
        b += 30

    return f"rgb({r}, {g}, {b})"
