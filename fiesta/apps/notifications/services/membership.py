from __future__ import annotations

import logging

from django.conf import settings

from apps.notifications.services.mailer import send_notification_email

logger = logging.getLogger(__name__)


def notify_new_membership(membership) -> None:
    """
    Called (via on_commit) when a new SectionMembership is created in UNCONFIRMED state.

    1. Send confirmation email to the new applicant (if section config allows).
    2. Send/enqueue digest email to all editors/admins (if section config allows).
    """
    section = membership.section

    try:
        config = section.sections_plugin_configuration
    except Exception:
        logger.debug("No SectionsConfiguration for section %s, skipping membership notifications", section)
        return

    if config.email_notify_member_on_received:
        _send_member_received_email(membership=membership, section=section)

    if config.email_notify_on_new_member:
        _enqueue_editor_digests(membership=membership, section=section, config=config)


def _send_member_received_email(*, membership, section) -> None:
    preferences_url = f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
    context = {
        "membership": membership,
        "section": section,
        "preferences_url": preferences_url,
    }
    send_notification_email(
        subject=f"{section} – Application received",
        recipient_email=membership.user.email,
        template_prefix="notifications/sections/membership_received",
        context=context,
        recipient_profile=membership.user.profile,
    )


def _enqueue_editor_digests(*, membership, section, config) -> None:
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

    for editor_membership in editors:
        editor = editor_membership.user

        try:
            profile = editor.profile
            prefs = SectionNotificationPreferences.objects.get(user=profile, section=section)
            if not prefs.notify_on_new_member_waiting:
                continue
        except SectionNotificationPreferences.DoesNotExist:
            pass  # Default is True — send
        except Exception:
            pass  # No profile or other issue — default to sending

        enqueue_delayed_notification(
            kind=NotificationKind.MEMBER_WAITING_DIGEST,
            recipient=profile,
            section=section,
            related_object=membership,
            send_after=send_after,
        )
