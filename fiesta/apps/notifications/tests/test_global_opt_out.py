from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.core import mail
from django.test import TestCase
from django.utils import timezone

from apps.accounts.models import UserProfile
from apps.notifications.models import NotificationKind, ScheduledNotification
from apps.notifications.services.mailer import send_notification_email
from apps.notifications.services.match import notify_buddy_match
from apps.notifications.services.scheduler import enqueue_delayed_notification
from apps.sections.tests.factories import KnownSectionFactory
from apps.utils.factories.accounts import UserFactory


def _make_buddy_config(notify=True, delay=timedelta(hours=1)):
    config = MagicMock()
    config.email_notify_on_match = notify
    config.email_notify_issuer_delay = delay
    return config


def _make_section_with_buddy_config(base_section, config):
    mock_section = MagicMock(spec=base_section.__class__)
    mock_section.pk = base_section.pk
    mock_section.space_slug = base_section.space_slug
    mock_section.__str__ = MagicMock(return_value=str(base_section))
    mock_section.buddy_system_configuration = config
    return mock_section


def _make_match_and_request(matcher, issuer):
    request_mock = MagicMock()
    request_mock.issuer = issuer

    match_mock = MagicMock()
    match_mock.matcher = matcher
    match_mock.request = request_mock

    return match_mock, request_mock


class GlobalOptOutNotificationsTestCase(TestCase):
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_opted_out_matcher_gets_no_immediate_email_but_issuer_is_still_enqueued(self, mock_send, mock_enqueue):
        matcher = UserFactory(profile=None)
        matcher_profile = UserProfile.objects.create(user=matcher)
        matcher_profile.email_notifications_enabled = False
        matcher_profile.save(update_fields=["email_notifications_enabled"])

        issuer = UserFactory(profile=None)
        UserProfile.objects.create(user=issuer)

        base_section = KnownSectionFactory()
        config = _make_buddy_config()
        section = _make_section_with_buddy_config(base_section, config)
        match, request = _make_match_and_request(matcher, issuer)

        with self.captureOnCommitCallbacks(execute=True):
            notify_buddy_match(match=match, request=request, section=section)

        mock_send.assert_not_called()
        mock_enqueue.assert_called_once()
        self.assertEqual(mock_enqueue.call_args.kwargs["kind"], NotificationKind.BUDDY_MATCHED_ISSUER)
        self.assertEqual(mock_enqueue.call_args.kwargs["recipient"], issuer)

    def test_enqueue_delayed_notification_skips_opted_out_and_creates_for_opted_in(self):
        section = KnownSectionFactory()
        related_object = section
        send_after = timezone.now() + timedelta(hours=1)

        opted_out_user = UserFactory(profile=None)
        opted_out_profile = UserProfile.objects.create(user=opted_out_user)
        opted_out_profile.email_notifications_enabled = False
        opted_out_profile.save(update_fields=["email_notifications_enabled"])

        result = enqueue_delayed_notification(
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
            recipient=opted_out_user,
            section=section,
            related_object=related_object,
            send_after=send_after,
        )

        self.assertIsNone(result)
        self.assertEqual(ScheduledNotification.objects.count(), 0)

        opted_in_user = UserFactory(profile=None)
        UserProfile.objects.create(user=opted_in_user)

        created = enqueue_delayed_notification(
            kind=NotificationKind.BUDDY_MATCHED_ISSUER,
            recipient=opted_in_user,
            section=section,
            related_object=related_object,
            send_after=send_after,
        )

        self.assertIsNotNone(created)
        assert created is not None
        self.assertEqual(ScheduledNotification.objects.count(), 1)
        self.assertEqual(created.recipient, opted_in_user)

    def test_send_notification_email_skips_opted_out_and_sends_for_opted_in(self):
        opted_out_user = UserFactory(profile=None)
        opted_out_profile = UserProfile.objects.create(user=opted_out_user)
        opted_out_profile.email_notifications_enabled = False
        opted_out_profile.save(update_fields=["email_notifications_enabled"])

        send_notification_email(
            subject="Matched",
            recipient_email=opted_out_user.email,
            template_prefix="notifications/base_email",
            context={
                "section": "ESN Test",
                "preferences_url": "https://example.com/preferences",
            },
            recipient_user=opted_out_user,
        )

        self.assertEqual(len(mail.outbox), 0)

        opted_in_user = UserFactory(profile=None)
        UserProfile.objects.create(user=opted_in_user)

        send_notification_email(
            subject="Matched",
            recipient_email=opted_in_user.email,
            template_prefix="notifications/base_email",
            context={
                "section": "ESN Test",
                "preferences_url": "https://example.com/preferences",
            },
            recipient_user=opted_in_user,
        )

        self.assertEqual(len(mail.outbox), 1)
