from __future__ import annotations

import djclick as click

from apps.utils.factories.faculty import FacultyFactory
from apps.utils.factories.universities import UniversityFactory


@click.command()
def seed():
    unis = UniversityFactory.create_batch(4)

    for uni in unis:
        FacultyFactory.create_batch(3, university=uni)
