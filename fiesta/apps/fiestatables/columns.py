import django_tables2 as tables
from django.db.models.fields.files import FieldFile
from django.utils.html import format_html


class ImageColumn(tables.Column):
    def render(self, value: FieldFile):
        return format_html('<img src="{}" class="h-12" />', value.url)

    def value(self, record, value):
        return value.url
