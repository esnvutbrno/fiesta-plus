from __future__ import annotations

import djclick as click


@click.command()
def seed():
    from apps.sections.services.sections_syncer import SectionsSyncer

    syncer = SectionsSyncer()

    syncer.sync()
