from django.contrib import admin
from apps.plugins.models import BasePluginConfiguration

from .models import OpenHoursConfiguration
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(OpenHoursConfiguration)
class OpenHoursConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
