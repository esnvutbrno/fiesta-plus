from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from uuid import UUID

from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.plugin_config import get_plugin_configuration
from apps.notifications.services.urls import preferences_url

if TYPE_CHECKING:
    from apps.sections.models import Section, SectionMembership, SectionsConfiguration

logger = logging.getLogger(__name__)


def notify_new_membership(membership: SectionMembership) -> None:
    """
    Called (via on_commit) when a new SectionMembership is created in UNCONFIRMED state.

    1. Send confirmation email to the new applicant (if section config allows).
    2. Send/enqueue digest email to all editors/admins (if section config allows).
    """
    section = membership.section

    config = get_plugin_configuration(section, "sections")
    if config is None:
        logger.debug("No SectionsConfiguration for section %s, skipping membership notifications", section)
        return

    if config.email_notify_member_on_received:
        _send_member_received_email(membership=membership, section=section)

    if config.email_notify_on_new_member:
        _enqueue_editor_digests(membership=membership, section=section, config=config)


def _send_member_received_email(*, membership: SectionMembership, section: Section) -> None:
    context = {
        "membership": membership,
        "section": section,
        "preferences_url": preferences_url(section),
    }
    send_notification_email(
        subject=f"{section} - Application received",
        recipient_email=membership.user.email,
        template_prefix="notifications/sections/membership_received",
        context=context,
        recipient_user=membership.user,
    )


def _enqueue_editor_digests(
    *,
    membership: SectionMembership,
    section: Section,
    config: SectionsConfiguration,
) -> None:
    from django.utils import timezone

    from apps.notifications.models import NotificationKind, SectionNotificationPreferences
    from apps.notifications.services.scheduler import enqueue_delayed_notification
    from apps.sections.models import SectionMembership

    send_after = timezone.now() + config.email_digest_interval

    editors = SectionMembership.objects.filter(
        section=section,
        state=SectionMembership.State.ACTIVE,
        role__in=[SectionMembership.Role.EDITOR, SectionMembership.Role.ADMIN],
    ).select_related("user")

    # Bulk-fetch preferences for all editors to avoid N+1 queries.
    editor_users = [m.user for m in editors]
    prefs_by_user: dict[UUID, SectionNotificationPreferences] = {
        p.user_id: p for p in SectionNotificationPreferences.objects.filter(user__in=editor_users, section=section)
    }

    for editor_membership in editors:
        editor = editor_membership.user

        prefs = prefs_by_user.get(editor.pk)
        if prefs is not None and not prefs.notify_on_new_member_waiting:
            continue
        # No prefs record → default is True (send).

        enqueue_delayed_notification(
            kind=NotificationKind.MEMBER_WAITING_DIGEST,
            recipient=editor,
            section=section,
            related_object=membership,
            send_after=send_after,
        )
