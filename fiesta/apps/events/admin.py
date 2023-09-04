from django.contrib import admin
from apps.plugins.models import BasePluginConfiguration

from .models import EventsConfiguration
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(EventsConfiguration)
class EventsConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
