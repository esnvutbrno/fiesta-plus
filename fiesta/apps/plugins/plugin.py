from abc import ABCMeta
from importlib import import_module
from typing import Iterable, Optional

from django.apps import AppConfig
from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, reverse


class PluginAppConfig(AppConfig, metaclass=ABCMeta):
    """
    Base app config for all pluginable applications.

    Optinonaly defines model of configuration, which has to inherit from BasePluginConfiguration -- in that case,
    plugin could be linked to model configuration. Otherwise, no configuration is provided.
    """

    title: str

    configuration_model: Optional[str] = None

    login_not_required_urls: list[str] = []

    membership_not_required_urls: list[str] = []

    def reverse(self, viewname, args=None, kwargs=None):
        """URL reverse for urls from this specific app (implicit namespaced)."""
        return reverse(f"{self.label}:{viewname}", args=args, kwargs=kwargs)

    @property
    def urlpatterns(self) -> Iterable[URLPattern]:
        urls: list[URLPattern] = import_module(f"{self.name}.urls").urlpatterns
        return tuple(
            map(
                lambda p: p if p.name in self.login_not_required_urls else URLPattern(
                    pattern=p.pattern,
                    callback=login_required(p.callback),
                    default_args=p.default_args,
                    name=p.name,
                ),
                urls,
            )
        )

    @property
    def url_prefix(self) -> str:
        """Defines prefix, under which are all urls included."""
        return self.label.replace("_", "-") + "/"


__all__ = ["PluginAppConfig"]
