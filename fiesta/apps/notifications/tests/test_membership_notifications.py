from __future__ import annotations

from datetime import timedelta
from unittest.mock import MagicMock, patch

from django.test import TestCase

from apps.notifications.models import ScheduledNotification
from apps.notifications.services.membership import notify_new_membership
from apps.notifications.tests.factories import SectionNotificationPreferencesFactory
from apps.sections.models import SectionMembership
from apps.utils.factories.accounts import UserFactory
from apps.utils.factories.sections import KnownSectionFactory, SectionMembershipWithUserFactory


def _make_sections_config(
    notify_member=True,
    notify_on_new_member=True,
    digest_interval=timedelta(hours=24),
):
    """Return a mock SectionsConfiguration object with the fields used by the service."""
    config = MagicMock()
    config.email_notify_member_on_received = notify_member
    config.email_notify_on_new_member = notify_on_new_member
    config.email_digest_interval = digest_interval
    return config


class NotifyNewMembershipTestCase(TestCase):
    def setUp(self):
        self.section = KnownSectionFactory()
        self.applicant = UserFactory(profile=None)
        self.membership = SectionMembershipWithUserFactory(
            section=self.section,
            user=self.applicant,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.UNCONFIRMED,
        )

    @patch("apps.notifications.services.membership.send_notification_email")
    def test_sends_received_email_to_applicant(self, mock_send):
        """Applicant receives a confirmation email when their membership application is registered."""
        config = _make_sections_config()
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args.kwargs
        self.assertIn("membership_received", call_kwargs["template_prefix"])
        self.assertEqual(call_kwargs["recipient_email"], self.applicant.email)

    @patch("apps.notifications.services.scheduler.enqueue_delayed_notification")
    @patch("apps.notifications.services.membership.send_notification_email")
    def test_enqueues_digest_for_editors(self, mock_send, mock_enqueue):
        """Active editors and admins each get a digest ScheduledNotification enqueued."""
        editor = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=editor,
            role=SectionMembership.Role.EDITOR,
            state=SectionMembership.State.ACTIVE,
        )

        admin_user = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=admin_user,
            role=SectionMembership.Role.ADMIN,
            state=SectionMembership.State.ACTIVE,
        )

        config = _make_sections_config()
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        # Both editor and admin should have enqueue called
        self.assertEqual(mock_enqueue.call_count, 2)
        for call in mock_enqueue.call_args_list:
            self.assertEqual(call.kwargs["kind"], ScheduledNotification.Kind.MEMBER_WAITING_DIGEST)
            self.assertEqual(call.kwargs["related_object"], self.membership)

    @patch("apps.notifications.services.scheduler.enqueue_delayed_notification")
    @patch("apps.notifications.services.membership.send_notification_email")
    def test_skips_non_editor_members(self, mock_send, mock_enqueue):
        """Regular members and international students do NOT get a digest notification."""
        regular_member = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=regular_member,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

        international = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=international,
            role=SectionMembership.Role.INTERNATIONAL,
            state=SectionMembership.State.ACTIVE,
        )

        config = _make_sections_config()
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.membership.send_notification_email")
    def test_config_disabled_skips_applicant_email(self, mock_send):
        """If config.email_notify_member_on_received=False, no confirmation email is sent to applicant."""
        config = _make_sections_config(notify_member=False)
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        mock_send.assert_not_called()

    @patch("apps.notifications.services.scheduler.enqueue_delayed_notification")
    @patch("apps.notifications.services.membership.send_notification_email")
    def test_config_disabled_skips_editor_digest(self, mock_send, mock_enqueue):
        """If config.email_notify_on_new_member=False, no digest notifications are enqueued for editors."""
        editor = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=editor,
            role=SectionMembership.Role.EDITOR,
            state=SectionMembership.State.ACTIVE,
        )

        config = _make_sections_config(notify_on_new_member=False)
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.scheduler.enqueue_delayed_notification")
    @patch("apps.notifications.services.membership.send_notification_email")
    def test_editor_opted_out_not_enqueued(self, mock_send, mock_enqueue):
        """Editor with notify_on_new_member_waiting=False does not receive a digest notification."""
        editor = UserFactory(profile=None)
        SectionMembershipWithUserFactory(
            section=self.section,
            user=editor,
            role=SectionMembership.Role.EDITOR,
            state=SectionMembership.State.ACTIVE,
        )
        SectionNotificationPreferencesFactory(
            user=editor,
            section=self.section,
            notify_on_new_member_waiting=False,
        )

        config = _make_sections_config()
        self.section.sections_plugin_configuration = config  # type: ignore[attr-defined]

        notify_new_membership(self.membership)

        mock_enqueue.assert_not_called()

    @patch("apps.notifications.services.membership.send_notification_email")
    def test_no_config_skips_all(self, mock_send):
        """If section has no SectionsConfiguration plugin, nothing is sent."""
        notify_new_membership(self.membership)

        mock_send.assert_not_called()
        self.assertEqual(ScheduledNotification.objects.count(), 0)
