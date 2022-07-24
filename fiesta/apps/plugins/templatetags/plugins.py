from __future__ import annotations

from typing import NamedTuple

from django import template

from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import Plugin
from apps.sections.models import SectionMembership

register = template.Library()


class PluginItemSpec(NamedTuple):
    title: str
    index_url: str
    urls: list[str]

    active: bool = False


@register.simple_tag(takes_context=True)
def active_plugins_as_navigation_items(context):
    request: HttpRequest = context["request"]

    current_plugin: Plugin | None = request.plugin
    membership: SectionMembership | None = request.membership

    if not membership:
        return []

    return [
        PluginItemSpec(
            apps.verbose_name,
            f"/{apps.url_prefix}",
            [
                # apps.reverse(pattern.name)
                # for pattern in apps.urlpatterns
            ],
            active=plugin == current_plugin,
        )
        for plugin in membership.section.plugins.filter(
            membership.available_plugins_filter
        )  # type: Plugin
        if (apps := plugin.app_config)
    ]
