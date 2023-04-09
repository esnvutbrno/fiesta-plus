from __future__ import annotations

import typing

from django import template
from django.urls import reverse

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.sections.models import SectionMembership

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

    items = []

    if not membership:
        return items

    items.extend(
        [
            nav_item
            for plugin in membership.section.plugins.filter(membership.available_plugins_filter)  # type: Plugin
            if (apps := plugin.app_config) and (nav_item := apps.as_navigation_item(request))  # type: PluginAppConfig
        ]
    )

    return items


@register.simple_tag(takes_context=True)
def get_home_url(context):
    request: HttpRequest = context["request"]

    if request.in_space_of_section:
        return request.in_space_of_section.section_home_url(request.membership)

    return reverse("public:home")
