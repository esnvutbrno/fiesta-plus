from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.accounts.services import UserProfileStateSynchronizer
from apps.plugins.models import Plugin
from apps.sections.models import SectionsConfiguration, SectionMembership
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.sections import SectionFactory, SectionMembershipFactory


class UserProfileStateSynchronizerTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(profile=None)
        self.profile: UserProfile = UserProfileFactory(user=self.user)
        self.section = SectionFactory()
        self.membership = SectionMembershipFactory(
            section=self.section,
            user=self.user,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

        self.configuration: SectionsConfiguration = (
            SectionsConfiguration.objects.create(
                name="Test configuration",
            )
        )
        self.plugin = Plugin.objects.create(
            state=Plugin.State.ENABLED,
            section=self.section,
            configuration=self.configuration,
            app_label="accounts",
        )

    def test_single_membership_with_required_attr(self):
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

    def test_single_membership_with_optional_attr(self):
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

    def test_single_membership_with_optional_attr_wo_sync(self):
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
