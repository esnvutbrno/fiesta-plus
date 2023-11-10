from __future__ import annotations

import dataclasses

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.apps import BuddySystemConfig
from apps.plugins.models import BasePluginConfiguration, Plugin
from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.sections.apps import SectionsConfig
from apps.sections.models import Section, SectionsConfiguration


@dataclasses.dataclass(frozen=True)
class SectionsPluginsValidator:
    """Defines relations between plugin configurations and validates them."""

    section: Section

    plugins: dict[str, Plugin]
    configurations: dict[str, BasePluginConfiguration]

    def check_validity(self):
        """Checks if all plugin configurations are valid."""
        for p in self.plugins.values():
            self._check_for_plugin(p)

    def _check_for_plugin(self, plugin: Plugin):
        match plugin.app_config:
            case BuddySystemConfig() | SectionsConfig():
                if not self.has_enabled_plugin(BuddySystemConfig):
                    return

                sections_conf: SectionsConfiguration = self.get_configuration(SectionsConfig)

                if not sections_conf.required_faculty:
                    raise ValidationError(
                        _(
                            "With enabled Buddy system plugin, you need to require faculty "
                            "in Section plugin configuration."
                        )
                    )

    def has_enabled_plugin(self, app: type[BasePluginAppConfig]):
        """Checks if plugin is enabled."""
        app_obj = all_plugins_mapped_to_class().get(app)

        return (plugin := self.plugins.get(app_obj.label)) and plugin.state != Plugin.State.DISABLED

    def get_configuration(self, app: type[BasePluginAppConfig]) -> BasePluginConfiguration | None:
        """Gets plugin configuration."""
        app_obj = all_plugins_mapped_to_class().get(app)

        return self.configurations.get(app_obj.label)

    @classmethod
    def for_changed_conf(cls, section: Section, conf: BasePluginConfiguration) -> SectionsPluginsValidator:
        """Creates validator for standard state, but a configuration has been changed."""
        plugin = conf.plugins.get(section=section)
        return cls(
            section=section,
            plugins={p.app_label: p for p in section.plugins.all()},
            configurations={p.app_label: p.configuration for p in section.plugins.all()} | {plugin.app_label: conf},
        )

    @classmethod
    def for_changed_plugin(cls, section: Section, plugin: Plugin) -> SectionsPluginsValidator:
        """Creates validator for standard state, but a plugin has been changed."""
        return cls(
            section=section,
            plugins={p.app_label: p for p in section.plugins.all()} | {plugin.app_label: plugin},
            configurations={p.app_label: p.configuration for p in section.plugins.all()},
        )
