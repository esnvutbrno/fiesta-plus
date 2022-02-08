from __future__ import annotations

from typing import NamedTuple

from django import template
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from django.views import View

from apps.plugins.middleware.plugin import HttpRequest

register = template.Library()


class BreadcrumbTitle(NamedTuple):
    title: str
    url: str


@register.simple_tag(takes_context=True)
def breadcrumbs(context: dict):
    req: HttpRequest = context.get("request")
    view: View | None = context.get("view")

    try:
        view_title = view.title
    except AttributeError:
        view_title = None

    return render_to_string(
        "fiesta/parts/breadcrumbs.html",
        context=dict(
            items=list(
                filter(
                    None,
                    [
                        # TODO: slash is not always the home page?
                        BreadcrumbTitle(_("Home"), "/"),
                        BreadcrumbTitle(apps.title, f"/{apps.url_prefix}")
                        if (plugin := req.plugin) and (apps := plugin.app_config)
                        else None,
                        BreadcrumbTitle(view_title, req.build_absolute_uri())
                        if view_title
                        else None,
                    ],
                )
            )
        ),
    )
