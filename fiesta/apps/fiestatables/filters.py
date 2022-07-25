from django.db.models.fields.files import FieldFile
from django.utils.html import format_html
from django_filters import FilterSet, DateFromToRangeFilter
from django_tables2 import Column

from apps.fiestaforms.forms import DateInput
from apps.fiestatables.forms import BaseFilterForm


class ImageColumn(Column):
    def render(self, value: FieldFile):
        return format_html('<img src="{}" class="h-12" />', value.url)


class BaseFilterSet(FilterSet):
    class Meta:
        form = BaseFilterForm


class ProperDateFromToRangeFilter(DateFromToRangeFilter):
    class field_class(DateFromToRangeFilter.field_class):
        class widget(DateFromToRangeFilter.field_class.widget):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.widgets = [DateInput() for w in self.widgets]
