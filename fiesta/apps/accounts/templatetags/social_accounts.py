from __future__ import annotations

from allauth.socialaccount import providers
from allauth.socialaccount.models import SocialApp
from django import template
from django.contrib.sites.models import Site

register = template.Library()


@register.simple_tag(takes_context=True)
def get_all_available_social_providers(context) -> list[SocialApp]:
    request = context["request"]

    site = Site.objects.get_current(request=request)

    return SocialApp.objects.filter(sites__id=site.id, provider__in=providers.registry.provider_map.keys())
