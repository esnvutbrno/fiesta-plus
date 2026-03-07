from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import patch

from django.contrib.contenttypes.models import ContentType
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.tests.factories import ScheduledNotificationFactory
from apps.sections.models import Section
from apps.utils.factories.accounts import UserFactory
from apps.utils.factories.sections import KnownSectionFactory

COMMAND_NAME = "send_scheduled_notifications"


class SendScheduledNotificationsTestCase(TestCase):
    def setUp(self):
        self.section: Section = KnownSectionFactory()
        self.recipient = UserFactory(profile=None)

    def _make_pending(self, kind=NotificationKind.MEMBER_WAITING_DIGEST, send_after=None):
        """Create a pending notification whose send_after is in the past by default."""
        return ScheduledNotificationFactory(
            recipient=self.recipient,
            section=self.section,
            kind=kind,
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
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
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
    def test_select_for_update_called_with_skip_locked(self, mock_send):
        """The command acquires row locks with skip_locked to support concurrent workers."""
        self._make_pending()

        with patch(
            "apps.notifications.management.commands.send_scheduled_notifications.ScheduledNotification.objects.select_for_update",
            wraps=ScheduledNotification.objects.select_for_update,
        ) as mock_select_for_update:
            call_command(COMMAND_NAME)

        mock_select_for_update.assert_called_once_with(skip_locked=True)

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_dry_run_logs_without_sending_or_marking_sent(self, mock_send):
        """Dry-run logs pending notifications but does not send or persist sent_at."""
        notification = self._make_pending()

        with self.assertLogs(
            "apps.notifications.management.commands.send_scheduled_notifications",
            level="INFO",
        ) as captured_logs:
            call_command(COMMAND_NAME, dry_run=True)

        notification.refresh_from_db()

        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.cancelled_at)
        self.assertIn("Dry-run: would send scheduled notification", "\n".join(captured_logs.output))
        mock_send.assert_not_called()

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_send_failure_does_not_mark_sent(self, mock_send):
        """When send_notification_email raises, sent_at must remain None (claim is rolled back)."""
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

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_send_failure_logs_error_and_continues(self, mock_send):
        """A send exception is logged and processing continues to the next notification."""
        first_recipient = UserFactory(profile=None)
        second_recipient = UserFactory(profile=None)
        first = ScheduledNotificationFactory(
            recipient=first_recipient,
            section=self.section,
            kind=NotificationKind.MEMBER_WAITING_DIGEST,
            send_after=timezone.now() - timedelta(minutes=5),
        )
        second = ScheduledNotificationFactory(
            recipient=second_recipient,
            section=self.section,
            kind=NotificationKind.MEMBER_WAITING_DIGEST,
            send_after=timezone.now() - timedelta(minutes=5),
        )

        def _side_effect(*, recipient_email, **kwargs):
            if recipient_email == first_recipient.email:
                raise Exception("SMTP exploded")
            return

        mock_send.side_effect = _side_effect

        with self.assertLogs(
            "apps.notifications.management.commands.send_scheduled_notifications",
            level="ERROR",
        ) as captured_logs:
            call_command(COMMAND_NAME)

        first.refresh_from_db()
        second.refresh_from_db()

        self.assertIsNone(first.sent_at)
        self.assertIsNotNone(second.sent_at)
        self.assertEqual(mock_send.call_count, 2)
        self.assertIn("Failed to send scheduled notification pk=", "\n".join(captured_logs.output))

    @patch("apps.notifications.management.commands.send_scheduled_notifications.send_notification_email")
    def test_batch_size_limits_processed_notifications(self, mock_send):
        """Batch size limits how many eligible notifications are sent in one run."""
        first = self._make_pending()
        second = self._make_pending()
        third = self._make_pending()

        call_command(COMMAND_NAME, batch_size=2)

        first.refresh_from_db()
        second.refresh_from_db()
        third.refresh_from_db()

        sent_count = ScheduledNotification.objects.filter(
            pk__in=[first.pk, second.pk, third.pk],
            sent_at__isnull=False,
        ).count()
        self.assertEqual(sent_count, 2)
        self.assertEqual(mock_send.call_count, 2)
