from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.plugins.models import BasePluginConfiguration

from .models import OpenHours, OpenHoursConfiguration
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(OpenHoursConfiguration)
class OpenHoursConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(OpenHours)
class OpenHours(ModelAdmin):
    list_display = ("section", "day_index", "from_time", "to_time", "enabled")

    list_filter = ("section", "day_index", "enabled")
