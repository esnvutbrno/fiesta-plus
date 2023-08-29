from __future__ import annotations

from django import template

from apps.accounts.models import User, UserProfile

# from apps.plugins.middleware.plugin import HttpRequest

register = template.Library()


@register.simple_tag
def get_user_picture(user: User | None):
    try:
        profile: UserProfile = user.profile
    except (UserProfile.DoesNotExist, AttributeError):
        return None

    return profile.picture

@register.simple_tag(takes_context=True)
def compute_profile_fullness(context: dict, profile: UserProfile) -> float:
    fields = profile._meta.get_fields()  # Get all field names of UserProfile
    empty_fields = 0

    for field in fields:
        field_value = getattr(profile, field.name, None)
        if field_value is None or field_value == '':
            empty_fields += 1

    return (len(fields) - empty_fields) / len(fields)

