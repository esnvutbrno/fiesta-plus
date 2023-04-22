from __future__ import annotations

from django_filters import DateFromToRangeFilter, FilterSet

from apps.fiestaforms.forms import DateInput
from apps.fiestatables.forms import BaseFilterForm


class BaseFilterSet(FilterSet):
    class Meta:
        form = BaseFilterForm


class ProperDateFromToRangeFilter(DateFromToRangeFilter):
    class field_class(DateFromToRangeFilter.field_class):
        class widget(DateFromToRangeFilter.field_class.widget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.widgets = [DateInput() for w in self.widgets]
