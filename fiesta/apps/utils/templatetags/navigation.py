from __future__ import annotations

import typing

from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse
from django.utils.http import urlencode

if typing.TYPE_CHECKING:
    from apps.plugins.middleware.plugin import HttpRequest
    from apps.plugins.models import Plugin
    from apps.plugins.plugin import BasePluginAppConfig
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

    if not membership:
        return []

    plugins: list[Plugin] = (
        section.enabled_plugins_for_privileged if membership.is_privileged else section.enabled_plugins
    )

    for plugin in plugins:
        apps: BasePluginAppConfig = plugin.app_config
        item = apps.as_navigation_item(request=request, bound_plugin=plugin)
        if item:
            yield item


@register.simple_tag(takes_context=True)
def get_home_url(context):
    """Called also from error pages, checks everything potentially set by middlewares."""
    url = reverse("public:home")
    try:
        request: HttpRequest = context["request"]
    except KeyError:
        return url

    try:
        membership: SectionMembership | None = request.membership
    except AttributeError:
        membership = None

    try:
        section: Section | None = request.in_space_of_section
    except AttributeError:
        section = None

    if section:
        url = request.in_space_of_section.section_home_url(membership)

    if url:
        return url

    return (
        reverse("account_login")
        + "?"
        + (
            urlencode(
                {
                    **request.GET,
                    REDIRECT_FIELD_NAME: request.GET.get(REDIRECT_FIELD_NAME) or request.path,
                }
            )
        )
    )
