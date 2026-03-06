from __future__ import annotations

import logging

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import ScheduledNotification
from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.scheduler import enqueue_delayed_notification

logger = logging.getLogger(__name__)


def _get_prefs(user, section):
    """Return SectionNotificationPreferences for user+section, or None if missing."""
    from apps.notifications.models import SectionNotificationPreferences

    try:
        profile = user.profile
    except Exception:
        return None

    try:
        return SectionNotificationPreferences.objects.get(user=profile, section=section)
    except SectionNotificationPreferences.DoesNotExist:
        return None


def _notify_match_enabled(prefs) -> bool:
    """Return True if user wants match notifications (default True when prefs missing)."""
    if prefs is None:
        return True
    return prefs.notify_on_match


def notify_buddy_match(*, match, request, section) -> None:
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
    if _notify_match_enabled(matcher_prefs):
        _send_buddy_matcher_email(match=match, request=request, section=section)

    issuer = request.issuer
    issuer_prefs = _get_prefs(issuer, section)
    if _notify_match_enabled(issuer_prefs):
        send_after = timezone.now() + config.email_notify_issuer_delay
        transaction.on_commit(
            lambda: enqueue_delayed_notification(
                kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
                recipient=issuer,
                section=section,
                related_object=match,
                send_after=send_after,
            )
        )


def _send_buddy_matcher_email(*, match, request, section) -> None:
    preferences_url = f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
    context = {
        "match": match,
        "request": request,
        "section": section,
        "preferences_url": preferences_url,
    }
    send_notification_email(
        subject=f"{section} \u2013 Your buddy request has been matched!",
        recipient_email=match.matcher.email,
        template_prefix="notifications/buddy_system/matched_matcher",
        context=context,
    )


def notify_pickup_match(*, match, request, section) -> None:
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
    if _notify_match_enabled(matcher_prefs):
        _send_pickup_matcher_email(match=match, request=request, section=section)

    issuer = request.issuer
    issuer_prefs = _get_prefs(issuer, section)
    if _notify_match_enabled(issuer_prefs):
        send_after = timezone.now() + config.email_notify_issuer_delay
        transaction.on_commit(
            lambda: enqueue_delayed_notification(
                kind=ScheduledNotification.Kind.PICKUP_MATCHED_ISSUER,
                recipient=issuer,
                section=section,
                related_object=match,
                send_after=send_after,
            )
        )


def _send_pickup_matcher_email(*, match, request, section) -> None:
    preferences_url = f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/"
    context = {
        "match": match,
        "request": request,
        "section": section,
        "preferences_url": preferences_url,
    }
    send_notification_email(
        subject=f"{section} \u2013 Your pickup request has been matched!",
        recipient_email=match.matcher.email,
        template_prefix="notifications/pickup_system/matched_matcher",
        context=context,
    )
