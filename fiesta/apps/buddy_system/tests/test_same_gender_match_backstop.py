from __future__ import annotations

from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch, BuddySystemConfiguration
from apps.plugins.models import Plugin
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.faculty import FacultyFactory
from apps.utils.factories.sections import KnownSectionFactory


class BuddyRequestMatchSameGenderBackstopTestCase(TestCase):
    """Covers enforcement seam #3: Django admin (and any other direct-save path), via
    BuddyRequestMatch.clean() -- the model-level backstop."""

    def setUp(self):
        self.faculty = FacultyFactory()
        self.section = KnownSectionFactory()

        self.configuration = BuddySystemConfiguration.objects.create(
            name="Test buddy config",
            section=self.section,
            enable_same_gender_matching=True,
        )
        Plugin.objects.create(
            state=Plugin.State.ENABLED,
            section=self.section,
            configuration=self.configuration,
            app_label="buddy_system",
        )

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
        return user

    def test_mismatched_gender_match_is_rejected(self):
        matcher = self._matcher(UserProfile.Gender.MALE)
        match = BuddyRequestMatch(request=self.request, matcher=matcher, matcher_faculty=self.faculty)

        with self.assertRaises(ValidationError):
            match.full_clean()

    def test_same_gender_match_passes(self):
        matcher = self._matcher(UserProfile.Gender.FEMALE)
        match = BuddyRequestMatch(request=self.request, matcher=matcher, matcher_faculty=self.faculty)

        try:
            match.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() raised unexpectedly: {e}")

    def test_mismatched_gender_allowed_when_toggle_disabled(self):
        self.configuration.enable_same_gender_matching = False
        self.configuration.save()

        matcher = self._matcher(UserProfile.Gender.MALE)
        match = BuddyRequestMatch(request=self.request, matcher=matcher, matcher_faculty=self.faculty)

        try:
            match.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() raised unexpectedly: {e}")

    def test_mismatched_gender_allowed_when_request_not_same_gender_only(self):
        self.request.same_gender_only = False
        self.request.save()

        matcher = self._matcher(UserProfile.Gender.MALE)
        match = BuddyRequestMatch(request=self.request, matcher=matcher, matcher_faculty=self.faculty)

        try:
            match.full_clean()
        except ValidationError as e:
            self.fail(f"full_clean() raised unexpectedly: {e}")
