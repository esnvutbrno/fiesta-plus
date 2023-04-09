from __future__ import annotations

from django.contrib import admin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import DashboardConfiguration
from apps.plugins.models import BasePluginConfiguration


@admin.register(DashboardConfiguration)
class DashboardConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True
