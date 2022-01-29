from abc import ABCMeta
from importlib import import_module
from typing import Optional

from django.apps import AppConfig
from django.urls import URLPattern, reverse


class PluginAppConfig(AppConfig, metaclass=ABCMeta):
    """
    Base app config for all pluginable applications.

    Optinonaly defines model of configuration, which has to inherit from BasePluginConfiguration -- in that case,
    plugin could be linked to model configuration. Otherwise, no configuration is provided.
    """

    configuration_model: Optional[str] = None

    def reverse(self, viewname, args=None, kwargs=None):
        """URL reverse for urls from this specific app (implicit namespaced)."""
        return reverse(f"{self.label}:{viewname}", args=args, kwargs=kwargs)

    @property
    def urlpatterns(self) -> list[URLPattern]:
        return import_module(f"{self.name}.urls").urlpatterns

    @property
    def url_prefix(self) -> str:
        """Defines prefix, undef which are all urls included."""
        return self.label.replace("_", "-") + "/"


__all__ = ["PluginAppConfig"]
