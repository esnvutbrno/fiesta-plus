from django.contrib import admin

from apps.plugins.models import BasePluginConfiguration
from .models import DashboardConfiguration
from ..plugins.admin import BaseChildConfigurationAdmin


@admin.register(DashboardConfiguration)
class DashboardConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
