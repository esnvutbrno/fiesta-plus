from __future__ import annotations

from django.contrib import admin
from mptt.admin import DraggableMPTTAdmin

from ..plugins.admin import BaseChildConfigurationAdmin
from .models import PagesConfiguration
from .models.page import Page
from apps.plugins.models import BasePluginConfiguration


@admin.register(PagesConfiguration)
class PagesConfigurationAdmin(BaseChildConfigurationAdmin):
    base_model = BasePluginConfiguration
    show_in_index = True


@admin.register(Page)
class PagesAdmin(DraggableMPTTAdmin):
    list_display = (
        "tree_actions",
        "indented_title",
        "default",
        "slug_path",
        "order",
        "section",
        # ...more fields if you feel like it...
    )
    list_display_links = ("indented_title",)
    list_filter = ["section"]
    expand_tree_by_default = True
