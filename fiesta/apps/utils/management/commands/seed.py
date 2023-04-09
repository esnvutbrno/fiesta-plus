from __future__ import annotations

import djclick as click
from click import secho

from apps.utils.factories.buddy_system import BuddyRequestWithKnownUserFactory


@click.command()
def seed():
    import factory
    from faker_education import SchoolProvider

    factory.Faker.add_provider(SchoolProvider)
    # pprint.pprint(SectionMembershipWithUserFactory.create_batch(15))
    secho(BuddyRequestWithKnownUserFactory.create_batch(15))
