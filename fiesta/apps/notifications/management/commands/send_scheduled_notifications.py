from __future__ import annotations

import contextlib
import logging
from typing import TYPE_CHECKING, Any, cast

from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.urls import preferences_url as build_preferences_url

if TYPE_CHECKING:
    from django.db.models import Model

    from apps.buddy_system.models import BuddyRequestMatch
    from apps.pickup_system.models import PickupRequestMatch
    from apps.sections.models import Section, SectionMembership

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Send all pending scheduled notifications whose send_after time has passed."

    def add_arguments(self, parser: object) -> None:
        parser.add_argument(
            "--batch-size",
            type=int,
            default=100,
            help="Maximum number of pending notifications to process in a single run.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Log pending notifications without sending or updating sent_at.",
        )

    def handle(self, *args: object, **options: object) -> None:
        batch_size = options["batch_size"]
        dry_run = options["dry_run"]
        now = timezone.now()

        # Dry-run: just log pending notifications without claiming them.
        if dry_run:
            pending_qs = ScheduledNotification.objects.filter(
                send_after__lte=now,
                sent_at__isnull=True,
                cancelled_at__isnull=True,
            ).select_related("recipient")[:batch_size]
            would_send = 0
            for notification in pending_qs:
                logger.info(
                    "Dry-run: would send scheduled notification pk=%s kind=%s",
                    notification.pk,
                    notification.kind,
                )
                would_send += 1
            self.stdout.write(self.style.SUCCESS(f"Dry-run complete: would send {would_send} notification(s)."))
            return

        # Phase 1: Atomically claim pending notifications by stamping sent_at.
        # select_for_update(skip_locked=True) + immediate UPDATE prevents concurrent
        # workers from picking the same rows (locks held only for the UPDATE, not I/O).
        with transaction.atomic():
            pending_qs = (
                ScheduledNotification.objects.select_for_update(skip_locked=True)
                .filter(
                    send_after__lte=now,
                    sent_at__isnull=True,
                    cancelled_at__isnull=True,
                )
                .order_by("send_after", "pk")
            )

            reserved_ids: list[int] = list(pending_qs.values_list("pk", flat=True)[:batch_size])
            if reserved_ids:
                ScheduledNotification.objects.filter(pk__in=reserved_ids).update(sent_at=now)

        if not reserved_ids:
            self.stdout.write("No pending notifications.")
            return

        logger.info("Claimed %d notification(s) for sending (batch size: %d)", len(reserved_ids), batch_size)

        # Phase 2: Send each notification outside any transaction (no DB locks during I/O).
        sent = 0
        skipped = 0
        failed = 0

        for notification_pk in reserved_ids:
            try:
                notification = ScheduledNotification.objects.select_related("recipient", "section").get(
                    pk=notification_pk
                )
            except ScheduledNotification.DoesNotExist:
                skipped += 1
                continue

            try:
                actually_sent = self._send(notification)

                if notification.cancelled_at is not None or not actually_sent:
                    # Notification was soft-cancelled during _send (e.g. related object deleted)
                    # or skipped (missing section/related_object/unknown kind).
                    # Roll back the claim so sent_at reflects that no email was actually sent.
                    ScheduledNotification.objects.filter(pk=notification_pk).update(sent_at=None)
                    skipped += 1
                    continue

                sent += 1

            except Exception:
                logger.exception("Failed to send scheduled notification pk=%s", notification.pk)
                # Roll back the claim so the notification can be retried next run.
                ScheduledNotification.objects.filter(pk=notification_pk).update(sent_at=None)
                failed += 1

        self.stdout.write(self.style.SUCCESS(f"Sent {sent} notification(s), skipped {skipped}, failed {failed}."))

    def _send(self, notification: ScheduledNotification) -> bool:
        # Resolve the related object via GenericFK
        related_object = self._resolve_related_object(notification)

        # If the notification was soft-cancelled during resolution (deleted related object), stop.
        if notification.cancelled_at is not None:
            return False

        section = notification.section
        if section is None:
            return False

        context: dict[str, Any] = {
            "notification": notification,
            "related_object": related_object,
            "section": section,
            "preferences_url": build_preferences_url(section),
        }

        kind = notification.kind

        if kind == NotificationKind.BUDDY_MATCHED_ISSUER:
            if related_object is None:
                return False
            self._send_buddy_matched_issuer(
                notification=notification,
                related_object=cast("BuddyRequestMatch", related_object),
                context=context,
                section=section,
            )
            return True

        if kind == NotificationKind.PICKUP_MATCHED_ISSUER:
            if related_object is None:
                return False
            self._send_pickup_matched_issuer(
                notification=notification,
                related_object=cast("PickupRequestMatch", related_object),
                context=context,
                section=section,
            )
            return True

        if kind == NotificationKind.MEMBER_WAITING_DIGEST:
            if related_object is None:
                return False
            self._send_member_joined_editors(
                notification=notification,
                related_object=cast("SectionMembership", related_object),
                context=context,
                section=section,
            )
            return True

        logger.warning("Unknown notification kind %r — skipping notification %s", kind, notification.pk)
        return False

    def _resolve_related_object(self, notification: ScheduledNotification) -> Model | None:
        """Return the related object for the notification, or None if it no longer exists."""
        if not notification.content_type or not notification.object_id:
            return None

        try:
            return notification.content_type.get_object_for_this_type(pk=notification.object_id)
        except ObjectDoesNotExist:
            logger.warning(
                "Scheduled notification %s: related object %s/%s no longer exists — soft-cancelling.",
                notification.pk,
                notification.content_type,
                notification.object_id,
            )
            notification.cancel()
            notification.save(update_fields=["cancelled_at", "modified"])
            return None

    def _send_buddy_matched_issuer(
        self,
        *,
        notification: ScheduledNotification,
        related_object: BuddyRequestMatch,
        context: dict[str, Any],
        section: Section,
    ) -> None:
        context["match"] = related_object
        with contextlib.suppress(AttributeError):
            context["request"] = related_object.request

        send_notification_email(
            subject=f"{section} - You've been matched with a buddy!",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/buddy_system/matched_issuer",
            context=context,
            recipient_user=notification.recipient,
        )

    def _send_pickup_matched_issuer(
        self,
        *,
        notification: ScheduledNotification,
        related_object: PickupRequestMatch,
        context: dict[str, Any],
        section: Section,
    ) -> None:
        context["match"] = related_object
        with contextlib.suppress(AttributeError):
            context["request"] = related_object.request

        send_notification_email(
            subject=f"{section} - Your airport pickup has been arranged!",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/pickup_system/matched_issuer",
            context=context,
            recipient_user=notification.recipient,
        )

    def _send_member_joined_editors(
        self,
        *,
        notification: ScheduledNotification,
        related_object: SectionMembership,
        context: dict[str, Any],
        section: Section,
    ) -> None:
        from apps.sections.models import SectionMembership

        waiting_count = SectionMembership.objects.filter(
            section=section,
            state=SectionMembership.State.UNCONFIRMED,
        ).count()

        context["waiting_count"] = waiting_count

        send_notification_email(
            subject=f"{section} - {waiting_count} member(s) waiting for confirmation",
            recipient_email=notification.recipient.email,
            template_prefix="notifications/sections/membership_pending",
            context=context,
            recipient_user=notification.recipient,
        )
