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
    # req: HttpRequest = context.get("request")

    # TODO: compute based on accounts conf and profile state

    return 0.77
