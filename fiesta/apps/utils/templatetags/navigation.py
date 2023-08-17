from __future__ import annotations

import typing

from django import template
from django.urls import reverse

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin
    from apps.sections.models import Section, SectionMembership

register = template.Library()


class NavigationItemSpec(typing.NamedTuple):
    title: str
    url: str
    children: list[NavigationItemSpec] = []

    active: bool = False


@register.simple_tag(takes_context=True)
def get_navigation_items(context):
    request: HttpRequest = context["request"]

    membership: SectionMembership | None = request.membership
    section: Section | None = request.in_space_of_section

    items = []

    if not membership:
        return items

    plugins: list[Plugin] = (
        section.enabled_plugins_for_privileged if membership.is_privileged else section.enabled_plugins
    )

    items.extend(
        [
            nav_item
            for plugin in plugins  # type: Plugin
            if (apps := plugin.app_config)
            and (nav_item := apps.as_navigation_item(request=request, bound_plugin=plugin))  # type: PluginAppConfig
        ]
    )

    return items


@register.simple_tag(takes_context=True)
def get_home_url(context):
    url = reverse("public:home")
    try:
        request: HttpRequest = context["request"]

        if request.in_space_of_section:
            url = request.in_space_of_section.section_home_url(request.membership)
    except KeyError:
        ...

    return url
