from __future__ import annotations

from collections import namedtuple

from django import template

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def active_plugins(context):
    request: HttpRequest = context["request"]

    # current_plugin: Plugin | None = request.plugin
    membership: SectionMembership | None = request.membership

    if not membership:
        return []

    PluginSpec = namedtuple("PluginSpec", "name urls")
    return [
        PluginSpec(
            plugin.app_config.title,
            [
                plugin.app_config.reverse(pattern.name)
                for pattern in plugin.app_config.urlpatterns
            ],
        )
        for plugin in membership.section.plugins.all()
    ]
