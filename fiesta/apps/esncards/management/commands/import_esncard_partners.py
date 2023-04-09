from __future__ import annotations

import djclick as click


@click.command()
def sync():
    from apps.esncards.services.esncard_partners_importer import EsnCardPartnersImporter

    importer = EsnCardPartnersImporter()

    importer.sync()
