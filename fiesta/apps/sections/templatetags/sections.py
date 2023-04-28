from __future__ import annotations

import typing

from django import template

from apps.esncards.models import ESNcardApplication
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership

register = template.Library()


@register.simple_tag(takes_context=True)
def get_section_statistics(context: dict):
    req: HttpRequest = context.get("request")

    class Stats(typing.NamedTuple):
        members: int
        unconfirmed_members: int
        alumni: int
        internationals: int
        internationals_wo_request: int
        unprocessed_esncard_applications: int

    return Stats(
        members=req.in_space_of_section.memberships.filter(
            state=SectionMembership.State.ACTIVE,
            role=SectionMembership.Role.MEMBER,
        ).count(),
        unconfirmed_members=req.in_space_of_section.memberships.filter(
            state=SectionMembership.State.UNCONFIRMED,
            role=SectionMembership.Role.MEMBER,
        ).count(),
        alumni=req.in_space_of_section.memberships.filter(
            # state=SectionMembership.State.ACTIVE,
            role=SectionMembership.Role.ALUMNI,
        ).count(),
        internationals=req.in_space_of_section.memberships.filter(
            state=SectionMembership.State.ACTIVE,
            role=SectionMembership.Role.INTERNATIONAL,
        ).count(),
        internationals_wo_request=req.in_space_of_section.memberships.filter(
            state=SectionMembership.State.ACTIVE,
            role=SectionMembership.Role.INTERNATIONAL,
        )
        .filter(
            user__buddy_system_issued_requests__isnull=True,
            user__esncard_applications__isnull=True,
        )
        .count(),
        unprocessed_esncard_applications=req.in_space_of_section.esncard_applications.filter(
            state__in=(
                ESNcardApplication.State.CREATED,
                ESNcardApplication.State.ACCEPTED,
            )
        ).count(),
    )
