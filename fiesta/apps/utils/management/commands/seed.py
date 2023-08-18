from __future__ import annotations

import djclick as click

from apps.accounts.models import User
from apps.esncards.models import ESNcardApplication
from apps.utils.factories.esncards import ESNCardApplicationFactory


@click.command()
def seed():
    users = User.objects.filter(memberships__role__in=["member", "international"]).distinct()

    for u in users:
        ESNCardApplicationFactory.create_batch(
            1,
            user=u,
            first_name=u.first_name,
            last_name=u.last_name,
            section=u.memberships.first().section,
            state=ESNcardApplication.State.CREATED,
        )
