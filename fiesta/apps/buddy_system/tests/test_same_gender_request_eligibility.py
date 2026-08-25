from __future__ import annotations

from types import SimpleNamespace

from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.buddy_system.models import BuddySystemConfiguration
from apps.buddy_system.views.request import NewBuddyRequestView
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.faculty import FacultyFactory
from apps.utils.factories.sections import KnownSectionFactory


class NewBuddyRequestSameGenderEligibilityTestCase(TestCase):
    """Covers the "hide unless eligible" rule on the new-request form, via
    NewBuddyRequestView._same_gender_option_eligible."""

    def setUp(self):
        self.faculty = FacultyFactory()
        self.section = KnownSectionFactory()
        self.configuration = BuddySystemConfiguration.objects.create(
            name="Test buddy config",
            section=self.section,
            enable_same_gender_matching=True,
        )

    def _view_for(self, user, configuration=None):
        view = NewBuddyRequestView()
        view.request = SimpleNamespace(
            user=user,
            plugin=SimpleNamespace(configuration=configuration if configuration is not None else self.configuration),
        )
        return view

    def _user_with_gender(self, gender):
        user = UserFactory(profile=None)
        UserProfileFactory(user=user, gender=gender, faculty=self.faculty)
        return user

    def test_eligible_when_gender_is_female_and_toggle_enabled(self):
        user = self._user_with_gender(UserProfile.Gender.FEMALE)

        self.assertTrue(self._view_for(user)._same_gender_option_eligible())

    def test_eligible_when_gender_is_male_and_toggle_enabled(self):
        user = self._user_with_gender(UserProfile.Gender.MALE)

        self.assertTrue(self._view_for(user)._same_gender_option_eligible())

    def test_not_eligible_when_gender_is_other(self):
        user = self._user_with_gender(UserProfile.Gender.OTHER)

        self.assertFalse(self._view_for(user)._same_gender_option_eligible())

    def test_not_eligible_when_gender_is_decline_to_state(self):
        user = self._user_with_gender(UserProfile.Gender.DECLINE_TO_STATE)

        self.assertFalse(self._view_for(user)._same_gender_option_eligible())

    def test_not_eligible_when_gender_is_blank(self):
        user = self._user_with_gender("")

        self.assertFalse(self._view_for(user)._same_gender_option_eligible())

    def test_not_eligible_when_toggle_disabled(self):
        self.configuration.enable_same_gender_matching = False
        self.configuration.save()
        user = self._user_with_gender(UserProfile.Gender.FEMALE)

        self.assertFalse(self._view_for(user)._same_gender_option_eligible())

    def test_not_eligible_without_profile(self):
        user = UserFactory(profile=None)

        self.assertFalse(self._view_for(user)._same_gender_option_eligible())
