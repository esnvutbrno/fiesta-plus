from __future__ import annotations

import django_tables2 as tables
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.db.models import Choices, Model
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html
from django_countries import countries
from django_countries.fields import Country
from django_tables2.columns import BoundColumn


# TODO: probably not needed anymore
class ImageColumn(tables.Column):
    def render(self, value: FieldFile):
        return format_html('<img src="{}" class="h-12" />', value.url)

    def value(self, record, value):
        return value.url


class AvatarColumn(ImageColumn):
    def render(self, value: FieldFile):
        return format_html(
            """
<div class="avatar">
    <div class="w-12 rounded-xl">
        <img src="{}" />
    </div>
</div>
""",
            value.url,
        )


class CountryColumn(tables.Column):
    attrs = {"td": {"data-flag": str(True).lower()}}

    def render(self, value):
        c_code = countries.by_name(value)
        return format_html(
            "<span title='{}'>{}</span>",
            value,
            Country(c_code).unicode_flag if c_code else value,
        )

    def value(self, value):
        return value


class NaturalDatetimeColumn(tables.Column):
    attrs = {"td": {"title": lambda bound_column, record: bound_column.accessor.resolve(record)}}

    def value(self, value):
        return value

    def render(self, value):
        return NaturalTimeFormatter.string_for(value)


class LabeledChoicesColumn(tables.Column):
    def __init__(
        self,
        choices: type[Choices],
        labels_replacements: dict[str, str] = None,
        *args,
        **kwargs,
    ):
        self._choices = choices
        self._labels_replacements = labels_replacements or dict()
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
