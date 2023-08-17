from __future__ import annotations

from django.contrib import admin
from django.contrib.admin import ModelAdmin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import OpenHours, OpenHoursConfiguration
from apps.plugins.models import BasePluginConfiguration


@admin.register(OpenHoursConfiguration)
class OpenHoursConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(OpenHours)
class OpenHoursAdmin(ModelAdmin):
    list_display = ("section", "day_index", "from_time", "to_time", "enabled")

    list_filter = ("section", "day_index", "enabled")
