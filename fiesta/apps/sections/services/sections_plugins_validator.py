from __future__ import annotations

import dataclasses

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.apps import BuddySystemConfig
from apps.pickup_system.apps import PickupSystemConfig
from apps.plugins.models import BasePluginConfiguration, Plugin
from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.sections.apps import SectionsConfig
from apps.sections.models import Section, SectionsConfiguration


@dataclasses.dataclass(frozen=True)
class SectionPluginsValidator:
    """Defines relations between plugin configurations and validates them."""

    section: Section

    plugins: dict[str, Plugin]
    configurations: dict[str, BasePluginConfiguration]

    def check_validity(self):
        """Checks if all plugin configurations are valid."""
        for p in self.plugins.values():
            self._check_for_plugin(p)

    def _check_for_plugin(self, plugin: Plugin):
        sections_conf: SectionsConfiguration = self.get_configuration(SectionsConfig)

        # TODO: would be better to refactor to some kind of matrix:
        #  FIELD_DEPENDENCIES = {
        #      BuddySystemConfig: (SectionsConfig, SectionsConfiguration.required_faculty, lambda v: v),
        #  }

        match plugin.app_config:
            case (BuddySystemConfig() | PickupSystemConfig()):
                self._check_field_dependency(
                    plugin=plugin,
                    field_value=sections_conf.required_faculty,
                    err=ValidationError(
                        _(
                            "With enabled {plugin} plugin, you need to have enabled "
                            "faculty requirement in the ESN Section plugin configuration."
                        ).format(plugin=plugin.app_config.verbose_name),
                    ),
                )
            case SectionsConfig():
                for cfg in (BuddySystemConfig, PickupSystemConfig):
                    app = all_plugins_mapped_to_class().get(cfg)
                    plugin = self.plugins.get(app.label)

                    if not plugin:
                        continue

                    self._check_field_dependency(
                        plugin=plugin,
                        field_value=sections_conf.required_faculty,
                        err=ValidationError(
                            _(
                                "With enabled {plugin} plugin, you need to have enabled "
                                "faculty requirement in the ESN Section plugin configuration."
                            ).format(plugin=app.verbose_name),
                        ),
                    )

    def _check_field_dependency(
        self,
        plugin: Plugin,
        field_value: bool,
        err: ValidationError,
    ):
        if not plugin:
            return

        if plugin.state == Plugin.State.DISABLED:
            return

        if field_value:
            return

        raise err

    def has_enabled_plugin(self, app: type[BasePluginAppConfig]):
        """Checks if plugin is enabled."""
        app_obj = all_plugins_mapped_to_class().get(app)

        return (plugin := self.plugins.get(app_obj.label)) and plugin.state != Plugin.State.DISABLED

    def get_configuration(self, app: type[BasePluginAppConfig]) -> BasePluginConfiguration | None:
        """Gets plugin configuration."""
        app_obj = all_plugins_mapped_to_class().get(app)

        return self.configurations.get(app_obj.label)

    @classmethod
    def for_changed_conf(cls, section: Section, conf: BasePluginConfiguration) -> SectionPluginsValidator:
        """Creates validator for standard state, but a configuration has been changed."""
        plugin = conf.plugins.get(section=section)
        return cls(
            section=section,
            plugins={p.app_label: p for p in section.plugins.all()},
            configurations={p.app_label: p.configuration for p in section.plugins.all()} | {plugin.app_label: conf},
        )

    @classmethod
    def for_changed_plugin(cls, section: Section, plugin: Plugin) -> SectionPluginsValidator:
        """Creates validator for standard state, but a plugin has been changed."""
        return cls(
            section=section,
            plugins={p.app_label: p for p in section.plugins.all()} | {plugin.app_label: plugin},
            configurations={p.app_label: p.configuration for p in section.plugins.all()},
        )
