from __future__ import annotations

from collections.abc import Iterable

from django import template

from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.breadcrumbs import BreadcrumbItem, push_breadcrumb_item

register = template.Library()


@register.simple_tag(takes_context=True)
def breadcrumb_items(context: dict):
    req: HttpRequest = context.get("request")

    if hasattr(req, "breadcrumbs"):
        return req.breadcrumbs

    try:
        view_titles = req.titles
    except AttributeError:
        view_titles = ()

    req.breadcrumbs = [
        BreadcrumbItem(item, req.build_absolute_uri()) if isinstance(item, str) else item() if callable(item) else item
        for item in filter(None, view_titles)
    ]

    return req.breadcrumbs


@register.simple_tag(takes_context=True)
def breadcrumb_push_current_plugin(context: dict):
    request: HttpRequest = context["request"]

    push_breadcrumb_item(request=request, item=request.plugin.app_config.verbose_name)

    return ""


@register.simple_tag(takes_context=True)
def breadcrumb_push_item(context: dict, item: str):
    request: HttpRequest = context["request"]

    push_breadcrumb_item(request=request, item=item)

    return ""


@register.filter
def join_breadcrumbs(items: Iterable[BreadcrumbItem], sep=" · "):
    return sep.join(map(lambda i: str(i() if callable(i) else i), items[::-1]))
