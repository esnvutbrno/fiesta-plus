from factory import SubFactory
from factory.django import DjangoModelFactory
from factory.fuzzy import FuzzyChoice

from apps.buddy_system.models import BuddyRequest
from apps.sections.models import Section


class BuddyRequestFactory(DjangoModelFactory):
    class Meta:
        model = BuddyRequest

    issuer = SubFactory(
        "apps.utils.factories.accounts.UserSingleMembershipFactory",
    )
    responsible_section = FuzzyChoice(
        Section.objects.all(),
    )
    state = BuddyRequest.State.CREATED
