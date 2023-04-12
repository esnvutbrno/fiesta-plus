from __future__ import annotations

from django import template
from django.urls import reverse

from apps.sections.middleware.section_space import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def section_membership_activation_url(context, membership: SectionMembership):
    request: HttpRequest = context["request"]

    return membership.section.section_base_url(request) + (
        membership.section.section_home_url(membership) or reverse("public:home")
    )
