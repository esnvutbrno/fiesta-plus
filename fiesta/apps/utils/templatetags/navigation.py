from __future__ import annotations

import typing

from django import template
from django.urls import reverse
from django.utils.translation import gettext as _

from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import Plugin
from apps.sections.models import SectionMembership

register = template.Library()


class NavigationItemSpec(typing.NamedTuple):
    title: str
    index_url: str
    urls: list[str]

    active: bool = False


@register.simple_tag(takes_context=True)
def get_navigation_items(context):
    request: HttpRequest = context["request"]

    current_plugin: Plugin | None = request.plugin
    membership: SectionMembership | None = request.membership

    items = []

    if not membership:
        return items

    if membership.is_privileged:
        # TODO: define these urls elsewhere
        items.append(
            NavigationItemSpec(
                _("Members"),
                reverse("sections:section-members"),
                [],
                request.resolver_match and request.resolver_match.route.replace("/", ":") == "sections:section-members",
            )
        )

    items.extend(
        [
            NavigationItemSpec(
                apps.verbose_name,
                f"/{apps.url_prefix}",
                [
                    # apps.reverse(pattern.name)
                    # for pattern in apps.urlpatterns
                    # if pattern.name
                ],
                active=plugin == current_plugin,
            )
            for plugin in membership.section.plugins.filter(membership.available_plugins_filter)  # type: Plugin
            if (apps := plugin.app_config) and apps.include_in_top_navigation  # type: PluginAppConfig
        ]
    )

    return items


@register.simple_tag(takes_context=True)
def get_home_url(context):
    request: HttpRequest = context["request"]

    if request.in_space_of_section:
        return request.in_space_of_section.section_home_url(request)

    return reverse("public:home")
