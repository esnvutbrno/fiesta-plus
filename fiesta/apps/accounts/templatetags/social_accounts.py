from __future__ import annotations

from operator import attrgetter

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.base import Provider
from django import template
from django.contrib.sites.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_all_available_social_providers(context) -> list[Provider]:
    request = context["request"]
    all_providers = providers.registry.get_list()

    site = Site.objects.get_current(request=request)

    all_available = SocialApp.objects.filter(
        sites__id=site.id, provider__in=tuple(map(attrgetter("id"), all_providers))
    ).values_list("provider", flat=True)

    return [p for p in all_providers if p.id in all_available]
