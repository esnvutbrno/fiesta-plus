from __future__ import annotations

from allauth.account.utils import get_next_redirect_url
from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse

from apps.sections.middleware.section_space import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def section_membership_activation_url(context, membership: SectionMembership):
    request: HttpRequest = context["request"]

    next_url = get_next_redirect_url(request, REDIRECT_FIELD_NAME) or ""

    return membership.section.section_base_url(request) + (
        next_url if next_url else (membership.section.section_home_url(membership) or reverse("public:home"))
    )
