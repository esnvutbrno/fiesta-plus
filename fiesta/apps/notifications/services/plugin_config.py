from __future__ import annotations

from typing import TYPE_CHECKING

from apps.plugins.models import Plugin

if TYPE_CHECKING:
    from apps.plugins.models import BasePluginConfiguration
    from apps.sections.models import Section


def get_plugin_configuration(section: Section, app_label: str) -> BasePluginConfiguration | None:
    """Return the configuration of the plugin identified by app_label enabled on section, or None."""
    try:
        return section.plugins.get(app_label=app_label).configuration
    except Plugin.DoesNotExist:
        return None
