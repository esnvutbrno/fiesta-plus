from __future__ import annotations

import typing
from abc import ABCMeta
from collections.abc import Iterable
from enum import StrEnum
from importlib import import_module

from django.apps import AppConfig
from django.contrib.auth.decorators import login_required
from django.urls import URLPattern, reverse

from apps.utils.templatetags.navigation import NavigationItemSpec

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models.plugin import Plugin


class BasePluginAppConfig(AppConfig, metaclass=ABCMeta):
    """
    Base app config for all pluginable applications.

    Optionally defines model of configuration, which has to inherit from BasePluginConfiguration -- in that case,
    plugin could be linked to model configuration. Otherwise, no configuration is provided.
    """

    class FeatureState(StrEnum):
        STABLE = "stable"
        EXPERIMENTAL = "experimental"
        DEPRECATED = "deprecated"

    FeatureState.do_not_call_in_templates = True  # django tweak to smooth usage in templates

    # name of plugin
    verbose_name: str

    # emoji for plugin
    emoji: str = ""

    # short description of plugin
    description: str = ""

    # model of configuration
    configuration_model: str | None = None

    # login required by default
    login_required = True

    # url names with access without login
    login_not_required_urls: list[str] = []

    # url names with access without membership
    membership_not_required_urls: list[str] = []

    # should the plugin be enforced for all sections?
    auto_enabled = False

    # controls the plugin_feature_state ribbon as a warning for users
    feature_state = FeatureState.STABLE

    # order of plugin in navigation
    order: int = 1000

    def reverse(self, viewname, args=None, kwargs=None):
        """URL reverse for urls from this specific app (implicit namespaced)."""
        return reverse(f"{self.label}:{viewname}", args=args, kwargs=kwargs)

    @property
    def urlpatterns(self) -> Iterable[URLPattern]:
        urls: list[URLPattern] = import_module(f"{self.name}.urls").urlpatterns
        return (
            tuple(
                map(
                    lambda p: (
                        p
                        if p.name in self.login_not_required_urls
                        else URLPattern(
                            pattern=p.pattern,
                            callback=login_required(p.callback),
                            default_args=p.default_args,
                            name=p.name,
                        )
                    ),
                    urls,
                )
            )
            if self.login_required
            else urls
        )

    @property
    def url_prefix(self) -> str:
        """Defines prefix, under which are all urls included."""
        return self.label.replace("_", "-") + "/"

    def as_navigation_item(self, request: HttpRequest, bound_plugin: Plugin) -> NavigationItemSpec | None:
        return NavigationItemSpec(
            self.verbose_name,
            f"/{self.url_prefix}",
            [],
            self.label == (request.plugin and request.plugin.app_label),
        )


__all__ = ["BasePluginAppConfig"]
