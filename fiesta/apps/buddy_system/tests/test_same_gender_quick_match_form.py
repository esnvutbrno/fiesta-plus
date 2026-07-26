from __future__ import annotations

from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.buddy_system.forms import QuickBuddyMatchForm
from apps.buddy_system.models import BuddyRequest
from apps.sections.models import SectionMembership
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.faculty import FacultyFactory
from apps.utils.factories.sections import KnownSectionFactory, SectionMembershipWithUserFactory


class QuickBuddyMatchFormSameGenderTestCase(TestCase):
    """Covers enforcement seam #2: editor quick-match, via QuickBuddyMatchForm.clean_matcher."""

    def setUp(self):
        self.faculty = FacultyFactory()
        self.section = KnownSectionFactory()

        issuer = UserFactory(profile=None)
        UserProfileFactory(user=issuer, gender=UserProfile.Gender.FEMALE, faculty=self.faculty)

        self.request = BuddyRequest.objects.create(
            issuer=issuer,
            responsible_section=self.section,
            issuer_faculty=self.faculty,
            note="hi",
            issuer_gender=UserProfile.Gender.FEMALE,
            same_gender_only=True,
        )

    def _matcher(self, gender):
        user = UserFactory(profile=None)
        UserProfileFactory(user=user, gender=gender, faculty=self.faculty)
        SectionMembershipWithUserFactory(
            user=user,
            section=self.section,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )
        return user

    def test_opposite_gender_matcher_is_rejected_when_enabled(self):
        matcher = self._matcher(UserProfile.Gender.MALE)

        form = QuickBuddyMatchForm(
            data={"matcher": matcher.pk},
            instance=self.request,
            same_gender_matching_enabled=True,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("matcher", form.errors)

    def test_same_gender_matcher_is_accepted_when_enabled(self):
        matcher = self._matcher(UserProfile.Gender.FEMALE)

        form = QuickBuddyMatchForm(
            data={"matcher": matcher.pk},
            instance=self.request,
            same_gender_matching_enabled=True,
        )

        self.assertTrue(form.is_valid(), form.errors)

    def test_opposite_gender_matcher_is_accepted_when_toggle_disabled(self):
        matcher = self._matcher(UserProfile.Gender.MALE)

        form = QuickBuddyMatchForm(
            data={"matcher": matcher.pk},
            instance=self.request,
            same_gender_matching_enabled=False,
        )

        self.assertTrue(form.is_valid(), form.errors)
