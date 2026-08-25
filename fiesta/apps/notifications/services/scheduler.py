from __future__ import annotations

import logging
from datetime import datetime
from typing import TYPE_CHECKING

from django.contrib.contenttypes.models import ContentType
from django.db import transaction

from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.services.opt_out import is_globally_opted_out

if TYPE_CHECKING:
    from django.db.models import Model

    from apps.accounts.models import User
    from apps.sections.models import Section

NotificationKindValue = NotificationKind | str

logger = logging.getLogger(__name__)


def enqueue_delayed_notification(
    *,
    kind: NotificationKindValue,
    recipient: User,
    section: Section,
    related_object: Model,
    send_after: datetime,
) -> ScheduledNotification | None:
    """
    Create a ScheduledNotification to be sent at send_after.

    If an unsent notification of the same kind already exists for this
    recipient + object, update its send_after time (upsert / digest logic).

    Uses select_for_update to prevent duplicate rows from concurrent requests.
    """
    if is_globally_opted_out(recipient):
        logger.info("Skipping scheduled notification for %s: global opt-out", recipient)
        return None

    ct = ContentType.objects.get_for_model(related_object)

    with transaction.atomic():
        existing = (
            ScheduledNotification.objects.select_for_update()
            .filter(
                kind=kind,
                recipient=recipient,
                content_type=ct,
                object_id=related_object.pk,
                sent_at__isnull=True,
                cancelled_at__isnull=True,
            )
            .first()
        )

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


def cancel_scheduled_notifications_for(related_object: Model) -> int:
    """
    Cancel all pending ScheduledNotifications linked to related_object.

    Returns the number of records cancelled.
    """
    from django.utils import timezone

    ct = ContentType.objects.get_for_model(related_object)
    now = timezone.now()

    count = ScheduledNotification.objects.filter(
        content_type=ct,
        object_id=related_object.pk,
        sent_at__isnull=True,
        cancelled_at__isnull=True,
    ).update(cancelled_at=now, modified=now)

    if count:
        logger.info("Cancelled %d scheduled notification(s) for %r", count, related_object)

    return count
