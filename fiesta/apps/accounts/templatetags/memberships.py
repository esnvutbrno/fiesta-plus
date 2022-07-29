from __future__ import annotations

from allauth.account.utils import get_next_redirect_url
from django import template
from django.contrib.auth import REDIRECT_FIELD_NAME

from apps.sections.middleware.section_space import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def section_membership_activation_url(context, section_membership: SectionMembership):
    request: HttpRequest = context["request"]

    return section_membership.section.section_url(request) + (
        get_next_redirect_url(request=request, redirect_field_name=REDIRECT_FIELD_NAME)
        or ""
    )
