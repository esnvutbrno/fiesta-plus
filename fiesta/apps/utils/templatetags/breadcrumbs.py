from __future__ import annotations

from typing import NamedTuple

from django import template
from django.http import HttpRequest

register = template.Library()


class BreadcrumbTitle(NamedTuple):
    title: str
    url: str


@register.simple_tag(takes_context=True)
def breadcrumb_items(context: dict):
    req: HttpRequest = context.get("request")

    if hasattr(req, "breadcrumbs"):
        return req.breadcrumbs

    try:
        view_titles = req.titles
    except AttributeError:
        view_titles = ()

    req.breadcrumbs = list(
        filter(
            None,
            [
                # TODO: slash is not always the home page?
                BreadcrumbTitle(req.membership.section, "/")
                if req.membership
                else None,  # TODO: eg "Home > Docs" doesn't make
                BreadcrumbTitle(apps.title, f"/{apps.url_prefix}")
                if (plugin := req.plugin) and (apps := plugin.app_config)
                else None,
            ]
            + [
                BreadcrumbTitle(title, req.build_absolute_uri())
                if isinstance(title, str)
                else title
                for title in view_titles
            ],
        )
    )
    return req.breadcrumbs


@register.simple_tag(takes_context=True)
def breadcrumb_push_item(context: dict, item: str):
    request: HttpRequest = context["request"]

    try:
        request.titles.append(item)
    except AttributeError:
        request.titles = [item]

    return ""
