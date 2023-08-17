from __future__ import annotations

import itertools

from django import template
from django.db.models import QuerySet


register = template.Library()


@register.filter
def group_day_table(open_hours: QuerySet):
    groups = itertools.groupby(open_hours, lambda x: x.day_index)
    return [(day_index, list(group)) for day_index, group in groups]
