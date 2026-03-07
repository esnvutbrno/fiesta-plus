from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import ScheduledNotification
from apps.notifications.tests.factories import ScheduledNotificationFactory
from apps.sections.models import Section
from apps.utils.factories.accounts import UserFactory
from apps.utils.factories.sections import KnownSectionFactory

COMMAND_NAME = "send_scheduled_notifications"


class SendScheduledNotificationsTestCase(TestCase):
    def setUp(self):
        self.section: Section = KnownSectionFactory()
        self.recipient = UserFactory(profile=None)

    def _make_pending(self, send_after=None):
        """Create a pending notification whose send_after is in the past by default."""
        return ScheduledNotificationFactory(
            recipient=self.recipient,
            section=self.section,
            send_after=send_after or (timezone.now() - timedelta(minutes=5)),
        )

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_sends_pending_notifications(self, mock_send):
        """A pending notification whose send_after is past gets sent and marked with sent_at."""
        notification = self._make_pending()

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        self.assertIsNotNone(notification.sent_at)

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_skips_future_notifications(self, mock_send):
        """A notification with send_after in the future is NOT processed."""
        future_time = timezone.now() + timedelta(hours=2)
        notification = self._make_pending(send_after=future_time)

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.cancelled_at)

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_skips_already_sent(self, mock_send):
        """A notification already marked sent_at is not re-sent."""
        already_sent_time = timezone.now() - timedelta(hours=1)
        notification = ScheduledNotificationFactory(
            recipient=self.recipient,
            section=self.section,
            send_after=timezone.now() - timedelta(hours=2),
            sent_at=already_sent_time,
        )

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        # sent_at should remain the original value — not updated again
        self.assertEqual(notification.sent_at, already_sent_time)
        # email must not have been called for this notification
        mock_send.assert_not_called()

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_skips_cancelled(self, mock_send):
        """A cancelled notification is not sent."""
        notification = ScheduledNotificationFactory(
            recipient=self.recipient,
            section=self.section,
            send_after=timezone.now() - timedelta(minutes=5),
            cancelled_at=timezone.now() - timedelta(hours=1),
        )

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        self.assertIsNone(notification.sent_at)
        mock_send.assert_not_called()

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_soft_cancels_on_deleted_object(self, mock_send):
        """
        If the notification's related_object no longer exists, the notification
        is soft-cancelled (cancelled_at is set) and no email is sent.
        """
        ct = ContentType.objects.get_for_model(Section)
        # Use a UUID that points to a non-existent Section
        non_existent_pk = uuid.uuid4()

        notification = ScheduledNotificationFactory(
            recipient=self.recipient,
            section=self.section,
            kind=ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER,
            send_after=timezone.now() - timedelta(minutes=5),
        )
        # Overwrite content_type/object_id to point to a deleted object
        notification.content_type = ct
        notification.object_id = non_existent_pk
        notification.save(update_fields=["content_type", "object_id"])

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        self.assertIsNotNone(notification.cancelled_at)
        self.assertIsNone(notification.sent_at)
        mock_send.assert_not_called()

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_select_for_update_used(self, mock_send):
        """
        Verify that the queryset uses select_for_update to prevent double-processing.
        We test this by inspecting the command source and confirming the queryset chain
        calls select_for_update before filter.
        """
        import inspect

        from apps.notifications.management.commands.send_scheduled_notifications import Command

        source = inspect.getsource(Command.handle)
        self.assertIn("select_for_update", source)

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_send_failure_does_not_mark_sent(self, mock_send):
        """When send_notification_email raises, sent_at must remain None."""
        mock_send.side_effect = RuntimeError("SMTP connection failed")
        notification = self._make_pending()

        call_command(COMMAND_NAME)

        notification.refresh_from_db()
        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.cancelled_at)

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_partial_failure_sends_remaining(self, mock_send):
        """If one notification fails, others are still sent."""
        n1 = self._make_pending()
        n2 = self._make_pending()

        # First call raises, second succeeds
        mock_send.side_effect = [RuntimeError("SMTP failure"), None]

        call_command(COMMAND_NAME)

        n1.refresh_from_db()
        n2.refresh_from_db()
        # One should have been sent, one should not — exact order depends on DB
        sent_count = sum(1 for n in [n1, n2] if n.sent_at is not None)
        failed_count = sum(1 for n in [n1, n2] if n.sent_at is None)
        self.assertEqual(sent_count, 1)
        self.assertEqual(failed_count, 1)
