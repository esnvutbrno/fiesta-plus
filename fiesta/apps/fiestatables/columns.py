from __future__ import annotations

import django_tables2 as tables
from django.contrib.humanize.templatetags.humanize import NaturalTimeFormatter
from django.db.models import Choices, Model
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django_tables2.columns import BoundColumn


class ImageColumn(tables.Column):
    def render(self, value: FieldFile):
        return format_html('<img src="{}" class="h-12" />', value.url)

    def value(self, record, value):
        return value.url


class ExpandableImageColumn(tables.TemplateColumn):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("template_name", "fiestatables/expandable_image_column.html")
        super().__init__(*args, **kwargs)

    def value(self, record, value):
        return value.url


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


class SelectionColumn(tables.TemplateColumn):
    action_button_text = _("process selected")

    def __init__(self, url, action_button_text=None, *args, **kwargs):
        if action_button_text:
            self.action_button_text = action_button_text

        self.action_url_name = url

        kwargs.setdefault("template_name", "fiestatables/selection_column.html")
        kwargs["orderable"] = False
        super().__init__(*args, **kwargs)
