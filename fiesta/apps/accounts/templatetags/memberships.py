from __future__ import annotations

from django import template
from django.urls import reverse

from apps.sections.middleware.section_space import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def section_membership_activation_url(context, membership: SectionMembership):
    request: HttpRequest = context["request"]

    # TODO: the next cannot blindly follow the source /path, because user probably does have
    #  a different role in target section, so it probably won't work
    # next_url = get_next_redirect_url(request, REDIRECT_FIELD_NAME) or ""
    #
    # return membership.section.section_base_url(request) + (
    #     next_url if next_url else (membership.section.section_home_url(membership) or reverse("public:home"))
    # )

    return membership.section.section_base_url(request) + (
        membership.section.section_home_url(membership) or reverse("public:home")
    )
