from __future__ import annotations

import typing

from django.db.models import Manager

from apps.plugins.plugin import PluginAppConfig
from apps.utils.models.query import get_single_object_or_none

if typing.TYPE_CHECKING:
    from apps.plugins.models import Plugin


class PluginManager(Manager):
    def get_by_app_config_or_none(self, plugin_app_config: PluginAppConfig) -> 'Plugin' | None:
        return get_single_object_or_none(
            self.get_queryset(),
            app_label=plugin_app_config.label,
        )
