import django_tables2 as tables
from django.db.models import Choices, Model
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html
from django_tables2.columns import BoundColumn


class ImageColumn(tables.Column):
    def render(self, value: FieldFile):
        return format_html('<img src="{}" class="h-12" />', value.url)

    def value(self, record, value):
        return value.url


class LabeledChoicesColumn(tables.Column):
    def __init__(
        self,
        choices: type[Choices],
        labels_replacements: dict[str, str],
        *args,
        **kwargs,
    ):
        self._choices = choices
        self._labels_replacements = labels_replacements
        super().__init__(*args, **kwargs)

    def render(self, bound_column: BoundColumn, record: Model):
        value = bound_column.accessor.resolve(record)
        return format_html(
            '<span title="{}">{}</span>',
            label := self._choices(value).label,
            self._labels_replacements.get(value) or label,
        )

    def value(self, record, value):
        return value
