import djclick as click
from click import secho

from apps.utils.factories.buddy_system import BuddyRequestWithKnownUserFactory


@click.command()
def seed():
    from faker_education import SchoolProvider
    import factory

    factory.Faker.add_provider(SchoolProvider)
    # pprint.pprint(SectionMembershipWithUserFactory.create_batch(15))
    secho(BuddyRequestWithKnownUserFactory.create_batch(15))
