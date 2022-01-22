from abc import ABCMeta
from typing import Optional

from django.apps import AppConfig


class PluginAppConfig(AppConfig, metaclass=ABCMeta):
    """
    Base app config for all pluginable applications.

    Optinonaly defines model of configuration, which has to inherit from BasePluginConfiguration -- in that case,
    plugin could be linked to model configuration. Otherwise, no configuration is provided.
    """

    configuration_model: Optional[str] = None

    @property
    def url_prefix(self) -> str:
        """Defines prefix,"""
        return self.label + "/"


__all__ = ["PluginAppConfig"]
