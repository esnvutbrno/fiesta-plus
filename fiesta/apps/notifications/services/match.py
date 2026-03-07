from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import NotificationKind
from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.scheduler import enqueue_delayed_notification

if TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
    from apps.notifications.models import SectionNotificationPreferences
    from apps.pickup_system.models import PickupRequest, PickupRequestMatch
    from apps.sections.models import Section

logger = logging.getLogger(__name__)


def _get_prefs(user: User, section: Section) -> SectionNotificationPreferences | None:
    """Return SectionNotificationPreferences for user+section, or None if missing."""
    from apps.notifications.models import SectionNotificationPreferences

    try:
        return SectionNotificationPreferences.objects.get(user=user, section=section)
    except SectionNotificationPreferences.DoesNotExist:
        return None


def _is_globally_opted_out(user: User) -> bool:
    """Return True if user has disabled email notifications globally."""
    try:
        return not user.profile.email_notifications_enabled
    except Exception:
        return False


def _notify_match_enabled(prefs: SectionNotificationPreferences | None) -> bool:
    """Return True if user wants match notifications (default True when prefs missing)."""
    if prefs is None:
        return True
    return prefs.notify_on_match


def notify_buddy_match(*, match: BuddyRequestMatch, request: BuddyRequest, section: Section) -> None:
    """
    Send immediate email to matcher; enqueue delayed email to issuer.

    Respects BuddySystemConfiguration.email_notify_on_match flag and user prefs.
    Called inside transaction.on_commit().
    """
    try:
        config = section.buddy_system_configuration
    except Exception:
        logger.debug("No BuddySystemConfiguration for section %s, skipping match notifications", section)
        return

    if not config.email_notify_on_match:
        return

    matcher = match.matcher
    matcher_prefs = _get_prefs(matcher, section)
    if _notify_match_enabled(matcher_prefs) and not _is_globally_opted_out(matcher):
        _send_buddy_matcher_email(match=match, request=request, section=section)

    issuer = request.issuer
    issuer_prefs = _get_prefs(issuer, section)
    if _notify_match_enabled(issuer_prefs):
        send_after = timezone.now() + config.email_notify_issuer_delay
        transaction.on_commit(
            lambda: enqueue_delayed_notification(
                kind=NotificationKind.BUDDY_MATCHED_ISSUER,
                recipient=issuer,
                section=section,
                related_object=match,
                send_after=send_after,
            )
        )


def _send_buddy_matcher_email(*, match: BuddyRequestMatch, request: BuddyRequest, section: Section) -> None:
    preferences_url = f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
    context = {
        "match": match,
        "request": request,
        "section": section,
        "preferences_url": preferences_url,
    }
    send_notification_email(
        subject=f"{section} – Your buddy request has been matched!",
        recipient_email=match.matcher.email,
        template_prefix="notifications/buddy_system/matched_matcher",
        context=context,
        recipient_user=match.matcher,
    )


def notify_pickup_match(*, match: PickupRequestMatch, request: PickupRequest, section: Section) -> None:
    """Same pattern as buddy, but for pickup_system."""
    try:
        config = section.pickup_system_configuration
    except Exception:
        logger.debug("No PickupSystemConfiguration for section %s, skipping", section)
        return

    if not config.email_notify_on_match:
        return

    matcher = match.matcher
    matcher_prefs = _get_prefs(matcher, section)
    if _notify_match_enabled(matcher_prefs) and not _is_globally_opted_out(matcher):
        _send_pickup_matcher_email(match=match, request=request, section=section)

    issuer = request.issuer
    issuer_prefs = _get_prefs(issuer, section)
    if _notify_match_enabled(issuer_prefs):
        send_after = timezone.now() + config.email_notify_issuer_delay
        transaction.on_commit(
            lambda: enqueue_delayed_notification(
                kind=NotificationKind.PICKUP_MATCHED_ISSUER,
                recipient=issuer,
                section=section,
                related_object=match,
                send_after=send_after,
            )
        )


def _send_pickup_matcher_email(*, match: PickupRequestMatch, request: PickupRequest, section: Section) -> None:
    preferences_url = f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
    context = {
        "match": match,
        "request": request,
        "section": section,
        "preferences_url": preferences_url,
    }
    send_notification_email(
        subject=f"{section} – Your pickup request has been matched!",
        recipient_email=match.matcher.email,
        template_prefix="notifications/pickup_system/matched_matcher",
        context=context,
        recipient_user=match.matcher,
    )
