from abc import ABCMeta
from typing import Optional

from django.apps import AppConfig


class PluginAppConfig(AppConfig, metaclass=ABCMeta):
    menu_template: str

    configuration_model: Optional[str] = None

    @classmethod
    def all_plugin_apps(cls) -> tuple["PluginAppConfig", ...]:
        from django.apps import apps

        return tuple(
            filter(lambda a: isinstance(a, PluginAppConfig), apps.get_app_configs())
        )

    @classmethod
    def all_plugins_as_choices(cls) -> list[tuple[str, str]]:
        return [(a.label, a.verbose_name) for a in cls.all_plugin_apps()]
