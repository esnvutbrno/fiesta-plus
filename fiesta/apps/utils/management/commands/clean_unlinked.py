import djclick as click
from click import secho

from apps.buddy_system.models import BuddyRequest
from apps.sections.models import Section, SectionUniversity


@click.command()
def seed():
    if input("You really want to delete all unlinked data? [yN] ") != "y":
        secho("Exiting")
        return

    sections = Section.objects.exclude(name="ESN VUT Brno")

    secho(BuddyRequest.objects.filter(responsible_section__in=sections).delete())
    secho(SectionUniversity.objects.filter(section__in=sections).delete())
    secho(SectionUniversity.objects.filter(section__in=sections).delete())

    secho(sections.delete())
