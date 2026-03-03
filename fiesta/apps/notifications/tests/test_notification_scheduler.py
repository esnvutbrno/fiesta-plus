from __future__ import annotations

import datetime

from django.test import TestCase
from django.utils import timezone

from apps.notifications.models import SectionNotificationPreferences
from apps.notifications.models.scheduled import NotificationKind
from apps.notifications.services import scheduler
from apps.sections.models import SectionMembership
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.sections import KnownSectionFactory, SectionMembershipWithUserFactory


class NotificationSchedulerBuddyMatchedTestCase(TestCase):
    """Tests for scheduling buddy-matched notifications."""

    def setUp(self):

        self.section = KnownSectionFactory()
        self.issuer_user = UserFactory()
        self.issuer_profile = UserProfileFactory(user=self.issuer_user)

        # Minimal fake BuddyRequest via a namespace object to avoid DB setup complexity
        self.request = _make_fake_request(
            issuer=self.issuer_user,
            section=self.section,
        )

    def test_schedule_creates_notification(self):
        """A new pending ScheduledNotification is created for the issuer's profile."""
        notification = scheduler.schedule_buddy_matched(
            buddy_request=self.request,
            delay=datetime.timedelta(seconds=0),
        )

        self.assertIsNotNone(notification)
        self.assertEqual(notification.kind, NotificationKind.BUDDY_MATCHED_ISSUER)
        self.assertEqual(notification.recipient, self.issuer_profile)
        self.assertEqual(notification.section, self.section)
        self.assertIsNone(notification.sent_at)
        self.assertIsNone(notification.cancelled_at)

    def test_schedule_twice_cancels_first(self):
        """Calling schedule twice cancels the first pending notification."""
        first = scheduler.schedule_buddy_matched(
            buddy_request=self.request,
            delay=datetime.timedelta(hours=1),
        )
        second = scheduler.schedule_buddy_matched(
            buddy_request=self.request,
            delay=datetime.timedelta(hours=1),
        )

        first.refresh_from_db()
        self.assertIsNotNone(first.cancelled_at)
        self.assertIsNone(second.cancelled_at)

    def test_cancel_buddy_matched_cancels_pending(self):
        """cancel_buddy_matched marks a pending notification as cancelled."""
        notification = scheduler.schedule_buddy_matched(
            buddy_request=self.request,
            delay=datetime.timedelta(hours=1),
        )

        cancelled_count = scheduler.cancel_buddy_matched(buddy_request=self.request)

        self.assertEqual(cancelled_count, 1)
        notification.refresh_from_db()
        self.assertIsNotNone(notification.cancelled_at)

    def test_cancel_already_sent_does_not_cancel(self):
        """Already-sent notifications are not affected by cancel_buddy_matched."""
        notification = scheduler.schedule_buddy_matched(
            buddy_request=self.request,
            delay=datetime.timedelta(hours=1),
        )
        # Simulate already sent
        notification.sent_at = timezone.now()
        notification.save(update_fields=["sent_at"])

        cancelled_count = scheduler.cancel_buddy_matched(buddy_request=self.request)

        self.assertEqual(cancelled_count, 0)
        notification.refresh_from_db()
        self.assertIsNone(notification.cancelled_at)

    def test_schedule_without_profile_returns_none(self):
        """schedule_buddy_matched returns None gracefully if issuer has no profile."""
        user_without_profile = UserFactory(profile=None)
        fake_request = _make_fake_request(issuer=user_without_profile, section=self.section)

        result = scheduler.schedule_buddy_matched(buddy_request=fake_request)

        self.assertIsNone(result)


class NotificationSchedulerMemberWaitingTestCase(TestCase):
    """Tests for the member-waiting digest scheduling."""

    def setUp(self):
        self.section = KnownSectionFactory()

        # Privileged member (editor)
        self.editor_user = UserFactory()
        self.editor_profile = UserProfileFactory(user=self.editor_user)
        self.editor_membership = SectionMembershipWithUserFactory(
            user=self.editor_user,
            section=self.section,
            role=SectionMembership.Role.EDITOR,
            state=SectionMembership.State.ACTIVE,
        )

        # New international member who just joined (trigger for the digest)
        self.new_user = UserFactory()
        self.new_membership = SectionMembershipWithUserFactory(
            user=self.new_user,
            section=self.section,
            role=SectionMembership.Role.INTERNATIONAL,
            state=SectionMembership.State.UNCONFIRMED,
        )

    def test_schedule_creates_digest_for_editors(self):
        """A digest notification is created for each active privileged member."""
        created = scheduler.schedule_member_waiting_digest(
            section=self.section,
            membership=self.new_membership,
            delay=datetime.timedelta(seconds=0),
        )

        self.assertEqual(len(created), 1)
        self.assertEqual(created[0].recipient, self.editor_profile)
        self.assertEqual(created[0].kind, NotificationKind.MEMBER_WAITING_DIGEST)

    def test_schedule_respects_opt_out(self):
        """Members who opted out of digest do not receive notifications."""
        SectionNotificationPreferences.objects.create(
            user=self.editor_profile,
            section=self.section,
            notify_on_new_member_waiting=False,
        )

        created = scheduler.schedule_member_waiting_digest(
            section=self.section,
            membership=self.new_membership,
            delay=datetime.timedelta(seconds=0),
        )

        self.assertEqual(len(created), 0)

    def test_schedule_does_not_duplicate_pending_digest(self):
        """A second digest is not created if a pending one already exists."""
        scheduler.schedule_member_waiting_digest(
            section=self.section,
            membership=self.new_membership,
            delay=datetime.timedelta(hours=1),
        )
        second = scheduler.schedule_member_waiting_digest(
            section=self.section,
            membership=self.new_membership,
            delay=datetime.timedelta(hours=1),
        )

        self.assertEqual(len(second), 0)

    def test_schedule_skips_non_privileged(self):
        """International/member-role users are NOT notified about waiting members."""
        regular_user = UserFactory()
        UserProfileFactory(user=regular_user)
        SectionMembershipWithUserFactory(
            user=regular_user,
            section=self.section,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

        created = scheduler.schedule_member_waiting_digest(
            section=self.section,
            membership=self.new_membership,
            delay=datetime.timedelta(seconds=0),
        )

        # Only the editor from setUp should be notified, not the plain member
        recipients = [n.recipient for n in created]
        self.assertIn(self.editor_profile, recipients)
        self.assertNotIn(regular_user.profile_or_none, recipients)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class _FakeRequest:
    """Lightweight stand-in for a BuddyRequest/PickupRequest in scheduler tests."""

    def __init__(self, issuer, section):
        self.issuer = issuer
        self.responsible_section = section


def _make_fake_request(*, issuer, section) -> _FakeRequest:
    return _FakeRequest(issuer=issuer, section=section)
