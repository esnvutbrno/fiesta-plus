from __future__ import annotations

from operator import attrgetter
from typing import Generic, Protocol, TypeVar

from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import BasePluginConfiguration
from apps.plugins.plugin import BasePluginAppConfig
from apps.plugins.utils import all_plugins_mapped_to_class
from apps.sections.models import Section, SectionMembership


class HasRequestProtocol(Protocol):
    request: HttpRequest


ConfigurationType = TypeVar("ConfigurationType", bound=BasePluginConfiguration)


class CheckEnabledPluginsViewMixin(Generic[ConfigurationType]):
    """Checks if plugin is enabled for current user."""

    def _is_plugin_enabled_for_user(self: HasRequestProtocol, app_type: type[BasePluginAppConfig]) -> bool:
        app = all_plugins_mapped_to_class().get(app_type)
        return app and app.label in self._get_enabled_plugin_app_labels(
            self.request.in_space_of_section,
            self.request.membership,
        )

    @staticmethod
    def _get_enabled_plugin_app_labels(
        in_space_of_section: Section,
        membership: SectionMembership,
    ) -> tuple[str, ...]:
        return tuple(
            map(
                attrgetter("app_label"),
                (
                    in_space_of_section.enabled_plugins_for_privileged
                    if membership.is_privileged
                    else in_space_of_section.enabled_plugins
                ),
            )
        )


class PluginConfigurationViewMixin(Generic[ConfigurationType]):
    @property
    def configuration(self: HasRequestProtocol) -> ConfigurationType:
        return self.request.plugin and self.request.plugin.configuration

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["configuration"] = self.configuration
        return data
