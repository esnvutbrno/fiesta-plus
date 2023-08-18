from __future__ import annotations

from django.contrib import admin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import ESNcardApplication, ESNcardsConfiguration
from .models.export import Export
from apps.plugins.models import BasePluginConfiguration


@admin.register(ESNcardsConfiguration)
class EsncardsConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(ESNcardApplication)
class ESNcardApplicationAdmin(admin.ModelAdmin):
    list_display = ["user", "section", "state", "created"]
    list_filter = ["section", "state"]
    raw_id_fields = ["user", "section"]


@admin.register(Export)
class ExportAdmin(admin.ModelAdmin):
    list_display = ["section", "state", "created"]
    list_filter = ["section", "state"]
