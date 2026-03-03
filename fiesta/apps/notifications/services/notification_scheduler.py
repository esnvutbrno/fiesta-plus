from __future__ import annotations

import datetime
import logging

from django.utils import timezone

from apps.notifications.models import ScheduledNotification
from apps.notifications.models.scheduled import NotificationKind

logger = logging.getLogger(__name__)


class NotificationScheduler:
    """
    Schedules transactional notifications to be sent after a delay.

    Separating scheduling from delivery allows editors to correct
    matching mistakes before the issuer receives any email.
    """

    MATCH_NOTIFICATION_DELAY = datetime.timedelta(hours=1)

    def schedule_buddy_matched(
        self,
        *,
        buddy_request,
        delay: datetime.timedelta | None = None,
    ) -> ScheduledNotification:
        """
        Schedule a 'buddy matched' email for the request issuer.

        Creates a pending ScheduledNotification that the management command
        will process once `send_after` has elapsed.  Idempotent per request:
        calling twice for the same request cancels any existing pending
        notification and creates a fresh one.
        """
        section = buddy_request.responsible_section
        recipient = buddy_request.issuer.profile if hasattr(buddy_request.issuer, "profile") else None

        if recipient is None:
            logger.warning(
                "Skipping buddy-matched notification for request %s — issuer has no profile",
                buddy_request.pk,
            )
            return None

        effective_delay = delay if delay is not None else self.MATCH_NOTIFICATION_DELAY

        self._cancel_pending(
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
        )

        notification = ScheduledNotification.objects.create(
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
            content_object=buddy_request,
            send_after=timezone.now() + effective_delay,
        )
        logger.info("Scheduled buddy-matched notification %s", notification.pk)
        return notification

    def schedule_pickup_matched(
        self,
        *,
        pickup_request,
        delay: datetime.timedelta | None = None,
    ) -> ScheduledNotification:
        """
        Schedule a 'pickup matched' email for the request issuer.

        Mirrors buddy-matched scheduling; see `schedule_buddy_matched` for details.
        """
        section = pickup_request.responsible_section
        recipient = pickup_request.issuer.profile if hasattr(pickup_request.issuer, "profile") else None

        if recipient is None:
            logger.warning(
                "Skipping pickup-matched notification for request %s — issuer has no profile",
                pickup_request.pk,
            )
            return None

        effective_delay = delay if delay is not None else self.MATCH_NOTIFICATION_DELAY

        self._cancel_pending(
            kind=NotificationKind.PICKUP_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
        )

        notification = ScheduledNotification.objects.create(
            kind=NotificationKind.PICKUP_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
            content_object=pickup_request,
            send_after=timezone.now() + effective_delay,
        )
        logger.info("Scheduled pickup-matched notification %s", notification.pk)
        return notification

    def schedule_member_waiting_digest(
        self,
        *,
        section,
        membership,
        delay: datetime.timedelta = datetime.timedelta(minutes=15),
    ) -> list[ScheduledNotification]:
        """
        Schedule a member-waiting digest for all privileged members of the section.

        Only creates notifications for users who have opted in via
        SectionNotificationPreferences; falls back to opt-in by default
        (i.e., if no preference row exists the notification is still created).
        """
        from apps.notifications.models import SectionNotificationPreferences
        from apps.sections.models import SectionMembership

        send_after = timezone.now() + delay

        privileged_memberships = membership.section.memberships.filter(
            role__in=[SectionMembership.Role.EDITOR, SectionMembership.Role.ADMIN],
            state=SectionMembership.State.ACTIVE,
        ).select_related("user__profile")

        created: list[ScheduledNotification] = []
        for privileged_membership in privileged_memberships:
            try:
                recipient = privileged_membership.user.profile
            except Exception:
                continue

            # Respect opt-out preference; default is opted-in (notify_on_new_member_waiting=True).
            try:
                prefs = SectionNotificationPreferences.objects.get(
                    user=recipient,
                    section=section,
                )
                if not prefs.notify_on_new_member_waiting:
                    continue
            except SectionNotificationPreferences.DoesNotExist:
                pass

            # De-duplicate: skip if a pending digest already exists for this recipient/section.
            already_pending = ScheduledNotification.objects.filter(
                kind=NotificationKind.MEMBER_WAITING_DIGEST,
                recipient=recipient,
                section=section,
                sent_at__isnull=True,
                cancelled_at__isnull=True,
            ).exists()
            if already_pending:
                continue

            notification = ScheduledNotification.objects.create(
                kind=NotificationKind.MEMBER_WAITING_DIGEST,
                recipient=recipient,
                section=section,
                content_object=membership,
                send_after=send_after,
            )
            created.append(notification)

        logger.info(
            "Scheduled %d member-waiting-digest notifications for section %s",
            len(created),
            section,
        )
        return created

    def cancel_buddy_matched(self, *, buddy_request) -> int:
        """
        Cancel pending buddy-matched notifications for the given request.

        Called when a match is deleted/reverted so the issuer never receives
        a stale 'you have been matched' email.
        """
        section = buddy_request.responsible_section
        recipient = buddy_request.issuer.profile if hasattr(buddy_request.issuer, "profile") else None

        if recipient is None:
            return 0

        return self._cancel_pending(
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
        )

    def cancel_pickup_matched(self, *, pickup_request) -> int:
        """
        Cancel pending pickup-matched notifications for the given request.
        """
        section = pickup_request.responsible_section
        recipient = pickup_request.issuer.profile if hasattr(pickup_request.issuer, "profile") else None

        if recipient is None:
            return 0

        return self._cancel_pending(
            kind=NotificationKind.PICKUP_MATCHED_ISSUER,
            recipient=recipient,
            section=section,
        )

    def _cancel_pending(self, *, kind: str, recipient, section) -> int:
        """
        Bulk-cancel all unsent notifications matching kind/recipient/section.

        Returns the count of cancelled notifications.
        """
        now = timezone.now()
        updated = (
            ScheduledNotification.objects.filter(
                kind=kind,
                recipient=recipient,
                section=section,
                sent_at__isnull=True,
                cancelled_at__isnull=True,
            )
            .exclude(send_after__lt=now)
            .update(cancelled_at=now)
        )
        if updated:
            logger.info("Cancelled %d pending %s notifications", updated, kind)
        return updated


scheduler = NotificationScheduler()

__all__ = ["NotificationScheduler", "scheduler"]
