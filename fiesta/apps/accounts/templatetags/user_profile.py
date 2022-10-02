from __future__ import annotations

from django import template

from apps.accounts.models import User, UserProfile

register = template.Library()


@register.simple_tag
def get_user_picture(user: User | None):
    try:
        profile: UserProfile = user.profile
    except (UserProfile.DoesNotExist, AttributeError):
        return None

    return profile.picture
