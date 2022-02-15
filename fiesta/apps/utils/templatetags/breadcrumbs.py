from __future__ import annotations

from typing import NamedTuple, Iterable

from django import template
from django.http import HttpRequest
from django.utils.encoding import force_str

register = template.Library()


class BreadcrumbItem(NamedTuple):
    title: str  # or lazy str
    url: str

    def __str__(self):
        return force_str(self.title)


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
                # BreadcrumbTitle(req.membership.section, "/")
                # if req.membership
                # else None,
                # TODO: eg "Home > Docs" doesn't make sense
                BreadcrumbItem(apps.title, f"/{apps.url_prefix}")
                if (plugin := req.plugin) and (apps := plugin.app_config)
                else None,
            ]
            + [
                BreadcrumbItem(title, req.build_absolute_uri())
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


@register.filter
def join_breadcrumbs(items: Iterable[BreadcrumbItem], sep=" · "):
    return sep.join(map(force_str, map(str, items[::-1])))
