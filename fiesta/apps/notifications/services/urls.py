from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings

if TYPE_CHECKING:
    from apps.sections.models import Section


def preferences_url(section: Section) -> str:
    """Build absolute URL to the notification preferences page for a given section."""
    return f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
