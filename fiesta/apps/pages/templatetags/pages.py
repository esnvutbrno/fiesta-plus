from __future__ import annotations

from django import template

from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.templatetags.navigation import NavigationItemSpec

register = template.Library()


@register.simple_tag(takes_context=True)
def get_navigation_items_for_pages(context: dict):
    request: HttpRequest = context["request"]

    return [
        NavigationItemSpec(
            p.title,
            url,
            [
                NavigationItemSpec(
                    sub.title,
                    sub_url,
                    [],
                    request.path.startswith(sub_url),
                )
                for sub in p.get_descendants()
                if (sub_url := sub.get_absolute_url(request))
            ],
            request.path.startswith(url),
        )
        for p in request.in_space_of_section.pages.filter(level=0).exclude(default=True)
        if (url := p.get_absolute_url(request))
    ]
