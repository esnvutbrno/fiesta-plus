from __future__ import annotations

import logging
from datetime import datetime

from django.contrib.contenttypes.models import ContentType

from apps.notifications.models import ScheduledNotification

logger = logging.getLogger(__name__)


def enqueue_delayed_notification(
    *,
    kind: str,
    recipient,
    section,
    related_object,
    send_after: datetime,
) -> ScheduledNotification:
    """
    Create a ScheduledNotification to be sent at send_after.

    If an unsent notification of the same kind already exists for this
    recipient + object, update its send_after time (upsert / digest logic).
    """
    ct = ContentType.objects.get_for_model(related_object)
    existing = ScheduledNotification.objects.filter(
        kind=kind,
        recipient=recipient,
        content_type=ct,
        object_id=related_object.pk,
        sent_at__isnull=True,
        cancelled_at__isnull=True,
    ).first()

    if existing:
        existing.send_after = send_after
        existing.save(update_fields=["send_after", "modified"])
        return existing

    return ScheduledNotification.objects.create(
        kind=kind,
        recipient=recipient,
        section=section,
        content_type=ct,
        object_id=related_object.pk,
        send_after=send_after,
    )


def cancel_scheduled_notifications_for(related_object) -> int:
    """
    Cancel all pending ScheduledNotifications linked to related_object.

    Returns the number of records cancelled.
    """
    ct = ContentType.objects.get_for_model(related_object)
    pending = ScheduledNotification.objects.filter(
        content_type=ct,
        object_id=related_object.pk,
        sent_at__isnull=True,
        cancelled_at__isnull=True,
    )

    count = 0
    for notification in pending:
        notification.cancel()
        notification.save(update_fields=["cancelled_at", "modified"])
        count += 1

    if count:
        logger.info("Cancelled %d scheduled notification(s) for %r", count, related_object)

    return count
