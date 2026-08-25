from __future__ import annotations

from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
from apps.fiestarequests.matching_policy import ManualByMemberMatchingPolicy
from apps.plugins.models import Plugin
from apps.sections.models import SectionMembership
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.faculty import FacultyFactory
from apps.utils.factories.sections import KnownSectionFactory, SectionMembershipWithUserFactory


class SameGenderMatchingPolicyTestCase(TestCase):
    """Covers enforcement seam #1: member self-match, via BaseMatchingPolicy.limit_requests."""

    def setUp(self):
        self.faculty = FacultyFactory()
        self.section = KnownSectionFactory()

        self.configuration = BuddySystemConfiguration.objects.create(
            name="Test buddy config",
            section=self.section,
            matching_policy=ManualByMemberMatchingPolicy.id,
            enable_same_gender_matching=True,
        )
        Plugin.objects.create(
            state=Plugin.State.ENABLED,
            section=self.section,
            configuration=self.configuration,
            app_label="buddy_system",
        )

        self.female_request = self._make_request(UserProfile.Gender.FEMALE, same_gender_only=True)
        self.male_request = self._make_request(UserProfile.Gender.MALE, same_gender_only=True)
        self.open_request = self._make_request(UserProfile.Gender.FEMALE, same_gender_only=False)

    def _make_request(self, gender, same_gender_only):
        issuer = UserFactory(profile=None)
        UserProfileFactory(user=issuer, gender=gender, faculty=self.faculty)
        SectionMembershipWithUserFactory(
            user=issuer,
            section=self.section,
            role=SectionMembership.Role.INTERNATIONAL,
            state=SectionMembership.State.ACTIVE,
        )
        return BuddyRequest.objects.create(
            issuer=issuer,
            responsible_section=self.section,
            issuer_faculty=self.faculty,
            note="hi",
            issuer_gender=gender,
            same_gender_only=same_gender_only,
        )

    def _matcher_membership(self, gender):
        user = UserFactory(profile=None)
        UserProfileFactory(user=user, gender=gender, faculty=self.faculty)
        return SectionMembershipWithUserFactory(
            user=user,
            section=self.section,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

    def _visible_requests(self, membership):
        return self.configuration.matching_policy_instance.limit_requests(
            qs=BuddyRequest.objects.all(),
            membership=membership,
        )

    def test_female_matcher_sees_female_only_and_open_requests(self):
        membership = self._matcher_membership(UserProfile.Gender.FEMALE)

        visible = self._visible_requests(membership)

        self.assertIn(self.female_request, visible)
        self.assertIn(self.open_request, visible)
        self.assertNotIn(self.male_request, visible)

    def test_male_matcher_is_blocked_from_female_only_request(self):
        membership = self._matcher_membership(UserProfile.Gender.MALE)

        visible = self._visible_requests(membership)

        self.assertNotIn(self.female_request, visible)
        self.assertIn(self.male_request, visible)
        self.assertIn(self.open_request, visible)

    def test_non_binary_matcher_is_blocked_from_all_gendered_requests(self):
        membership = self._matcher_membership(UserProfile.Gender.OTHER)

        visible = self._visible_requests(membership)

        self.assertNotIn(self.female_request, visible)
        self.assertNotIn(self.male_request, visible)
        self.assertIn(self.open_request, visible)

    def test_toggle_disabled_makes_all_requests_visible(self):
        self.configuration.enable_same_gender_matching = False
        self.configuration.save()

        membership = self._matcher_membership(UserProfile.Gender.MALE)

        visible = self._visible_requests(membership)

        self.assertIn(self.female_request, visible)
        self.assertIn(self.male_request, visible)
        self.assertIn(self.open_request, visible)
