from __future__ import annotations

from django import template

from apps.accounts.forms.profile_factory import UserProfileFormFactory
from apps.accounts.models import User, UserProfile
from apps.sections.models import SectionMembership

# from apps.plugins.middleware.plugin import HttpRequest

register = template.Library()


@register.simple_tag
def get_user_picture(user: User | None):
    try:
        profile: UserProfile = user.profile
    except (UserProfile.DoesNotExist, AttributeError):
        return None

    return profile.picture


@register.simple_tag
def get_user_status_ring_css_for_user(membership: SectionMembership | None):
    return (
        {
            SectionMembership.Role.ADMIN: "ring ring-primary",
            SectionMembership.Role.EDITOR: "ring ring-secondary",
            SectionMembership.Role.MEMBER: "ring ring-gray-400",
            SectionMembership.Role.INTERNATIONAL: "",
        }.get(membership.role)
        if membership
        else ""
    )


@register.simple_tag
def compute_profile_fullness(user: User) -> float:
    fields = UserProfileFormFactory.get_form_fields(user)  # Get all field names of UserProfile
    empty_fields = 0

    for field in fields:
        field_value = getattr(user.profile, field, None)
        if field_value is None or field_value == "":  # So far it's not possible to have a field with False value
            empty_fields += 1

    return (len(fields) - empty_fields) / len(fields)
