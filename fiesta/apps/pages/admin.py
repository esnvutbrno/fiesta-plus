from __future__ import annotations

from django.contrib import admin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import PagesConfiguration
from .models.page import Page
from apps.plugins.models import BasePluginConfiguration


@admin.register(PagesConfiguration)
class PagesConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(Page)
class PagesAdmin(admin.ModelAdmin):
    ...
