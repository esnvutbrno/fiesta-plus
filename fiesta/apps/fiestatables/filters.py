from __future__ import annotations

import typing

from django_filters import DateFromToRangeFilter, FilterSet

from apps.fiestaforms.forms import DateInput
from apps.fiestatables.forms import BaseFilterForm


class BaseFilterSet(FilterSet):
    class Meta:
        form = BaseFilterForm


def exclude_filters(filterset_class: type[BaseFilterSet], exclude: typing.Iterable[str]) -> type[BaseFilterSet]:
    """Takes base filteset class and returns new one with excluded filters."""

    class FilterSetWithExcludedFilters(filterset_class):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            for field_name in exclude:
                del self.filters[field_name]

    return FilterSetWithExcludedFilters


class ProperDateFromToRangeFilter(DateFromToRangeFilter):
    class field_class(DateFromToRangeFilter.field_class):
        class widget(DateFromToRangeFilter.field_class.widget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.widgets = [DateInput() for w in self.widgets]
