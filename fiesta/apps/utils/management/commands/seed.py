import djclick as click

from apps.utils.factories.buddy_system import BuddyRequestFactory
from apps.utils.factories.sections import SectionMembershipFactory


@click.command()
def seed():
    from faker_education import SchoolProvider
    import factory

    factory.Faker.add_provider(SchoolProvider)
    SectionMembershipFactory.create_batch(15)
    BuddyRequestFactory.create_batch(15)
