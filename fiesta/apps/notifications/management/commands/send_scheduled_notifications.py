from __future__ import annotations

import contextlib
import logging

from django.conf import settings
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.services.mailer import send_notification_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send all pending scheduled notifications whose send_after time has passed."

    def handle(self, *args, **options) -> None:
        # Phase 1: Reserve notifications in a short transaction.
        # select_for_update(skip_locked=True) ensures concurrent runs don't pick the same rows.
        reserved_ids: list[int] = []
        with transaction.atomic():
            reserved_ids = list(
                ScheduledNotification.objects.select_for_update(skip_locked=True)
                .filter(
                    send_after__lte=timezone.now(),
                    sent_at__isnull=True,
                    cancelled_at__isnull=True,
                )
                .values_list("pk", flat=True)
            )

        if not reserved_ids:
            self.stdout.write("No pending notifications.")
            return

        # Phase 2: Send each notification outside any transaction so DB locks are not held during I/O.
        sent = 0
        skipped = 0

        for notification_pk in reserved_ids:
            try:
                notification = ScheduledNotification.objects.select_related("recipient", "section").get(
                    pk=notification_pk
                )
            except ScheduledNotification.DoesNotExist:
                skipped += 1
                continue

            # Skip if another process already handled it between Phase 1 and now.
            if notification.sent_at is not None or notification.cancelled_at is not None:
                skipped += 1
                continue

            try:
                self._send(notification)

                if notification.cancelled_at is not None:
                    # Notification was soft-cancelled during _send (e.g. related object deleted).
                    skipped += 1
                    continue

                # Phase 3: Mark as sent in a short transaction.
                notification.sent_at = timezone.now()
                notification.save(update_fields=["sent_at", "modified"])
                sent += 1

            except Exception:
                logger.exception("Failed to send scheduled notification pk=%s", notification.pk)
                skipped += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} notification(s), skipped {skipped}."))

    def _send(self, notification: ScheduledNotification) -> None:
        # Resolve the related object via GenericFK
        related_object = self._resolve_related_object(notification)

        # If the notification was soft-cancelled during resolution (deleted related object), stop.
        if notification.cancelled_at is not None:
            return

        section = notification.section
        preferences_url = (
            f"https://{section.space_slug}.{settings.ROOT_DOMAIN}/notifications/preferences/" if section else ""
        )

        context = {
            "notification": notification,
            "related_object": related_object,
            "section": section,
            "preferences_url": preferences_url,
        }

        kind = notification.kind

        if kind == NotificationKind.BUDDY_MATCHED_ISSUER:
            self._send_buddy_matched_issuer(notification=notification, related_object=related_object, context=context)

        elif kind == NotificationKind.PICKUP_MATCHED_ISSUER:
            self._send_pickup_matched_issuer(notification=notification, related_object=related_object, context=context)

        elif kind == NotificationKind.MEMBER_WAITING_DIGEST:
            self._send_member_waiting_digest(notification=notification, section=section, context=context)

        else:
            logger.warning("Unknown notification kind %r — skipping notification %s", kind, notification.pk)

    def _resolve_related_object(self, notification: ScheduledNotification):
        """Return the related object for the notification, or None if it no longer exists."""
        if not notification.content_type or not notification.object_id:
            return None

        try:
            return notification.content_type.get_object_for_this_type(pk=notification.object_id)
        except Exception:
            logger.warning(
                "Scheduled notification %s: related object %s/%s no longer exists — soft-cancelling.",
                notification.pk,
                notification.content_type,
                notification.object_id,
            )
            notification.cancel()
            notification.save(update_fields=["cancelled_at", "modified"])
            return None

    def _send_buddy_matched_issuer(self, *, notification, related_object, context) -> None:
        if related_object is None:
            return

        context["match"] = related_object
        with contextlib.suppress(AttributeError):
            context["request"] = related_object.request

        send_notification_email(
            subject=f"{notification.section} – You've been matched with a buddy!",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/buddy_system/matched_issuer",
            context=context,
            recipient_user=notification.recipient,
        )

    def _send_pickup_matched_issuer(self, *, notification, related_object, context) -> None:
        if related_object is None:
            return

        context["match"] = related_object
        with contextlib.suppress(AttributeError):
            context["request"] = related_object.request

        send_notification_email(
            subject=f"{notification.section} – Your airport pickup has been arranged!",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/pickup_system/matched_issuer",
            context=context,
            recipient_user=notification.recipient,
        )

    def _send_member_waiting_digest(self, *, notification, section, context) -> None:
        waiting_count = 0
        try:
            from apps.sections.models import SectionMembership

            waiting_count = SectionMembership.objects.filter(
                section=section,
                state=SectionMembership.State.UNCONFIRMED,
            ).count()
        except Exception:
            pass

        context["waiting_count"] = waiting_count

        send_notification_email(
            subject=f"{section} – {waiting_count} member(s) waiting for confirmation",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/sections/membership_pending",
            context=context,
            recipient_user=notification.recipient,
        )
