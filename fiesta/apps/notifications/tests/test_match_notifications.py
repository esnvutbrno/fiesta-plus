from __future__ import annotations

import uuid
from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.notifications.models import ScheduledNotification
from apps.notifications.services.match import notify_buddy_match, notify_pickup_match
from apps.notifications.tests.factories import SectionNotificationPreferencesFactory
from apps.utils.factories.accounts import UserFactory
from apps.utils.factories.sections import KnownSectionFactory


def _make_buddy_config(notify=True, delay=timedelta(hours=1)):
    """Return a mock BuddySystemConfiguration with the fields used by the service."""
    config = MagicMock()
    config.email_notify_on_match = notify
    config.email_notify_issuer_delay = delay
    return config


def _make_pickup_config(notify=True, delay=timedelta(hours=1)):
    """Return a mock PickupSystemConfiguration with the fields used by the service."""
    config = MagicMock()
    config.email_notify_on_match = notify
    config.email_notify_issuer_delay = delay
    return config


def _make_match_and_request(matcher, issuer):
    """Return simple mock match and request objects suitable for service calls."""
    request_mock = MagicMock()
    request_mock.issuer = issuer

    match_mock = MagicMock()
    match_mock.pk = uuid.uuid4()
    match_mock.matcher = matcher
    match_mock.matcher.email = matcher.email
    match_mock.request = request_mock

    return match_mock, request_mock


class NotifyBuddyMatchTestCase(TestCase):
    def setUp(self):
        self.base_section = KnownSectionFactory()
        self.matcher = UserFactory(profile=None)
        self.issuer = UserFactory(profile=None)
        self.match, self.request_obj = _make_match_and_request(self.matcher, self.issuer)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_sends_immediate_matcher_email(self, mock_send, mock_get_config):
        """Matcher receives an immediate email when a buddy match is created."""
        mock_get_config.return_value = _make_buddy_config()

        notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        self.assertIn("matched_matcher", call_kwargs["template_prefix"])
        self.assertEqual(call_kwargs["recipient_email"], self.matcher.email)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_enqueues_issuer_notification(self, mock_send, mock_enqueue, mock_get_config):
        """Issuer gets enqueue_delayed_notification called when a buddy match is created."""
        mock_get_config.return_value = _make_buddy_config()

        with self.captureOnCommitCallbacks(execute=True):
            notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_enqueue.assert_called_once()
        call_kwargs = mock_enqueue.call_args.kwargs
        self.assertEqual(call_kwargs["kind"], ScheduledNotification.Kind.BUDDY_MATCHED_ISSUER)
        self.assertEqual(call_kwargs["recipient"], self.issuer)
        self.assertEqual(call_kwargs["related_object"], self.match)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_config_disabled_skips_all(self, mock_send, mock_enqueue, mock_get_config):
        """If config.email_notify_on_match=False, no email is sent and no notification is enqueued."""
        mock_get_config.return_value = _make_buddy_config(notify=False)

        with self.captureOnCommitCallbacks(execute=True):
            notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_not_called()
        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_matcher_opted_out_no_immediate_email(self, mock_send, mock_enqueue, mock_get_config):
        """If matcher has prefs with notify_on_match=False, no immediate email is sent to them."""
        SectionNotificationPreferencesFactory(
            user=self.matcher,
            section=self.base_section,
            notify_on_match=False,
        )

        mock_get_config.return_value = _make_buddy_config()

        notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        # No immediate email should have been sent to the matcher
        for call in mock_send.call_args_list:
            self.assertNotEqual(call.kwargs.get("recipient_email"), self.matcher.email)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_issuer_opted_out_no_scheduled(self, mock_send, mock_enqueue, mock_get_config):
        """If issuer has prefs with notify_on_match=False, no delayed notification is enqueued for them."""
        SectionNotificationPreferencesFactory(
            user=self.issuer,
            section=self.base_section,
            notify_on_match=False,
        )

        mock_get_config.return_value = _make_buddy_config()

        with self.captureOnCommitCallbacks(execute=True):
            notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.match.send_notification_email")
    def test_buddy_match_no_config_skips_all(self, mock_send):
        """If section has no buddy_system Plugin enabled, nothing is sent."""
        # Real section has no buddy_system Plugin row — get_plugin_configuration returns None
        notify_buddy_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_not_called()
        self.assertEqual(ScheduledNotification.objects.count(), 0)


class NotifyPickupMatchTestCase(TestCase):
    def setUp(self):
        self.base_section = KnownSectionFactory()
        self.matcher = UserFactory(profile=None)
        self.issuer = UserFactory(profile=None)
        self.match, self.request_obj = _make_match_and_request(self.matcher, self.issuer)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_pickup_match_sends_immediate_matcher_email(self, mock_send, mock_get_config):
        """Matcher receives an immediate email when a pickup match is created."""
        mock_get_config.return_value = _make_pickup_config()

        notify_pickup_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        self.assertIn("matched_matcher", call_kwargs["template_prefix"])
        self.assertEqual(call_kwargs["recipient_email"], self.matcher.email)

    @patch("apps.notifications.services.match.get_plugin_configuration")
    @patch("apps.notifications.services.match.enqueue_delayed_notification")
    @patch("apps.notifications.services.match.send_notification_email")
    def test_pickup_match_config_disabled_skips_all(self, mock_send, mock_enqueue, mock_get_config):
        """If config.email_notify_on_match=False, no email and no scheduled notification for pickup."""
        mock_get_config.return_value = _make_pickup_config(notify=False)

        with self.captureOnCommitCallbacks(execute=True):
            notify_pickup_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_not_called()
        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.match.send_notification_email")
    def test_pickup_match_no_config_skips_all(self, mock_send):
        """If section has no pickup_system Plugin enabled, nothing is sent."""
        notify_pickup_match(match=self.match, request=self.request_obj, section=self.base_section)

        mock_send.assert_not_called()
        self.assertEqual(ScheduledNotification.objects.count(), 0)
