from __future__ import annotations

import djclick as click

from apps.utils.factories.faculty import FacultyFactory


@click.command()
def seed():
    click.secho(f"{FacultyFactory.create_batch(10)}")
