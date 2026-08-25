from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from apps.accounts.models import User


def is_globally_opted_out(user: User) -> bool:
    """Return True if the user has disabled email notifications globally."""
    return hasattr(user, "profile") and not user.profile.email_notifications_enabled
