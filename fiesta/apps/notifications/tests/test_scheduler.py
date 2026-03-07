from __future__ import annotations

from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import ScheduledNotification
from apps.notifications.services.scheduler import cancel_scheduled_notifications_for, enqueue_delayed_notification
from apps.notifications.tests.factories import ScheduledNotificationFactory
from apps.sections.models import Section
from apps.utils.factories.accounts import UserFactory
from apps.utils.factories.sections import KnownSectionFactory


class EnqueueDelayedNotificationTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(profile=None)
        self.section: Section = KnownSectionFactory()
        self.send_after = timezone.now() + timedelta(hours=1)

    def test_enqueue_creates_new_notification(self):
        """Calling enqueue creates a ScheduledNotification with the correct fields."""
        notification = enqueue_delayed_notification(
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            recipient=self.user,
            section=self.section,
            related_object=self.section,  # use Section as a simple related_object
            send_after=self.send_after,
        )

        self.assertIsNotNone(notification.pk)
        self.assertEqual(notification.kind, ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER)
        self.assertEqual(notification.recipient, self.user)
        self.assertEqual(notification.section, self.section)
        self.assertEqual(notification.send_after, self.send_after)
        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.cancelled_at)

    def test_enqueue_upserts_existing_pending(self):
        """Calling enqueue again for the same recipient+object updates send_after instead of creating a duplicate."""
        first = enqueue_delayed_notification(
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            recipient=self.user,
            section=self.section,
            related_object=self.section,
            send_after=self.send_after,
        )

        later_time = self.send_after + timedelta(hours=2)
        second = enqueue_delayed_notification(
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            recipient=self.user,
            section=self.section,
            related_object=self.section,
            send_after=later_time,
        )

        # Should be the same DB record
        self.assertEqual(first.pk, second.pk)
        self.assertEqual(ScheduledNotification.objects.count(), 1)
        second.refresh_from_db()
        self.assertEqual(second.send_after, later_time)

    def test_enqueue_does_not_upsert_sent(self):
        """If an existing notification is already sent, a new one is created instead of updating."""
        # Create an already-sent notification
        sent_notification = ScheduledNotificationFactory(
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            recipient=self.user,
            section=self.section,
            object_id=self.section.pk,
            sent_at=timezone.now() - timedelta(hours=1),
        )
        # Point to same section as related object
        from django.contrib.contenttypes.models import ContentType

        sent_notification.content_type = ContentType.objects.get_for_model(self.section)
        sent_notification.save()

        new_notification = enqueue_delayed_notification(
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            recipient=self.user,
            section=self.section,
            related_object=self.section,
            send_after=self.send_after,
        )

        # A brand-new record should have been created
        self.assertNotEqual(sent_notification.pk, new_notification.pk)
        self.assertEqual(ScheduledNotification.objects.count(), 2)


class CancelScheduledNotificationsTestCase(TestCase):
    def setUp(self):
        self.section: Section = KnownSectionFactory()

    def test_cancel_cancels_pending(self):
        """cancel_scheduled_notifications_for marks pending notifications as cancelled."""
        user = UserFactory(profile=None)
        notification = ScheduledNotificationFactory(
            recipient=user,
            section=self.section,
            object_id=self.section.pk,
        )
        from django.contrib.contenttypes.models import ContentType

        notification.content_type = ContentType.objects.get_for_model(self.section)
        notification.save()

        count = cancel_scheduled_notifications_for(self.section)

        self.assertEqual(count, 1)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.cancelled_at)

    def test_cancel_skips_already_sent(self):
        """cancel_scheduled_notifications_for does not touch notifications that are already sent."""
        user = UserFactory(profile=None)
        from django.contrib.contenttypes.models import ContentType

        notification = ScheduledNotificationFactory(
            recipient=user,
            section=self.section,
            object_id=self.section.pk,
            sent_at=timezone.now(),
        )
        notification.content_type = ContentType.objects.get_for_model(self.section)
        notification.save()

        count = cancel_scheduled_notifications_for(self.section)

        self.assertEqual(count, 0)
        notification.refresh_from_db()
        self.assertIsNone(notification.cancelled_at)

    def test_cancel_returns_count(self):
        """cancel_scheduled_notifications_for returns the exact number of records cancelled."""
        from django.contrib.contenttypes.models import ContentType

        ct = ContentType.objects.get_for_model(self.section)
        users = [UserFactory(profile=None) for _ in range(3)]

        for user in users:
            n = ScheduledNotificationFactory(
                recipient=user,
                section=self.section,
                object_id=self.section.pk,
            )
            n.content_type = ct
            n.save()

        count = cancel_scheduled_notifications_for(self.section)
        self.assertEqual(count, 3)
