import factory
from django.test import TestCase

from apps.accounts.models import UserProfile
from apps.sections.models import SectionMembership
from apps.utils.factories.accounts import UserFactory, UserProfileFactory
from apps.utils.factories.sections import (
    KnownSectionFactory,
    SectionMembershipWithUserFactory,
)


class UserProfileStateSynchronizerSingleMembershipTestCase(TestCase):
    def setUp(self):
        self.user = UserFactory(profile=None)
        self.profile: UserProfile = UserProfileFactory(user=self.user)
        self.sections = KnownSectionFactory.build_batch(2)

        self.memberships = SectionMembershipWithUserFactory.build_batch(
            2,
            section=factory.Iterator(self.sections, cycle=False),
            user=self.user,
            role=SectionMembership.Role.MEMBER,
            state=SectionMembership.State.ACTIVE,
        )

        # self.configurations: SectionsConfiguration = (
        #     SectionsConfiguration.objects.create(
        #         name="Test configuration",
        #     )
        # )
        # self.plugins = Plugin.objects.create(
        #     state=Plugin.State.ENABLED,
        #     section=self.section,
        #     configuration=self.configuration,
        #     app_label="accounts",
        # )
        # self.country = 'CZ'

    # def test_two_required_confs(self):
    #     print(self.sections)
    #     self.assertTrue(True)
