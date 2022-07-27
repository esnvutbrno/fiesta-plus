import djclick as click

from apps.utils.factories.buddy_system import BuddyRequestFactory
from apps.utils.factories.sections import SectionMembershipFactory


@click.command()
def seed():
    SectionMembershipFactory.create_batch(15)
    BuddyRequestFactory.create_batch(15)
