from __future__ import annotations

from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.accounts.services import UserProfileStateSynchronizer
from apps.plugins.models import Plugin
from apps.sections.models import SectionMembership, SectionsConfiguration
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.sections import KnownSectionFactory, SectionMembershipWithUserFactory


class UserProfileStateSynchronizerSingleMembershipTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(profile=None)
        self.profile: UserProfile = UserProfileFactory(user=self.user)
        self.section = KnownSectionFactory()
        self.membership = SectionMembershipWithUserFactory(
            section=self.section,
            user=self.user,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

        self.configuration: SectionsConfiguration = SectionsConfiguration.objects.create(
            name="Test configuration",
        )
        self.plugin = Plugin.objects.create(
            state=Plugin.State.ENABLED,
            section=self.section,
            configuration=self.configuration,
            app_label="accounts",
        )
        self.country = "CZ"

    def test_required_attr(self):
        """
        Tests user with single membership to have incomplete porfile after requiring it from section and running
        the synchronizer.
        """
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it incomplete
        self.profile.nationality = None
        self.profile.save()
        # and required
        self.configuration.required_nationality = True
        self.configuration.save()

        # run synchronizer
        UserProfileStateSynchronizer.on_user_profile_update(self.profile)
        # should be incomplete
        self.assertEqual(self.profile.state, UserProfile.State.INCOMPLETE)

    def test_optional_attr(self):
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it without nationality
        self.profile.nationality = None
        self.profile.save()
        # and optional
        self.configuration.required_nationality = None
        self.configuration.save()

        # run synchronizer
        UserProfileStateSynchronizer.on_user_profile_update(self.profile)
        # should stay complete
        self.assertEqual(self.profile.state, UserProfile.State.COMPLETE)

    def test_optional_attr_wo_sync(self):
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it without nationality
        self.profile.nationality = None
        self.profile.save()
        # and optional
        self.configuration.required_nationality = True
        self.configuration.save()

        # not run of sync
        # should stay complete
        self.assertEqual(self.profile.state, UserProfile.State.COMPLETE)

    def test_sync_keeps_required_value(self):
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it without nationality
        self.profile.nationality = self.country
        self.profile.save()
        # and optional
        self.configuration.required_nationality = True
        self.configuration.save()

        # run synchronizer
        UserProfileStateSynchronizer.on_user_profile_update(self.profile)

        # should stay complete with filled nationality
        self.assertEqual(self.profile.state, UserProfile.State.COMPLETE)
        self.assertEqual(self.profile.nationality, self.country)

    def test_syncer_keeps_not_required_value(self):
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it without nationality
        self.profile.nationality = self.country
        self.profile.save()
        # and optional
        self.configuration.required_nationality = False
        self.configuration.save()

        # run synchronizer
        UserProfileStateSynchronizer.on_user_profile_update(self.profile)

        # should stay complete with filled nationality
        self.assertEqual(self.profile.state, UserProfile.State.COMPLETE)
        self.assertEqual(self.profile.nationality, self.country)

    def test_syncer_keeps_not_wanted_value(self):
        # default is fine
        self.profile.state = UserProfile.State.COMPLETE
        # make it without nationality
        self.profile.nationality = self.country
        self.profile.save()
        # and optional
        self.configuration.required_nationality = None
        self.configuration.save()

        # run synchronizer
        UserProfileStateSynchronizer.on_user_profile_update(self.profile)

        # should stay complete with filled nationality
        self.assertEqual(self.profile.state, UserProfile.State.COMPLETE)
        self.assertEqual(self.profile.nationality, self.country)
