from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

import djclick as click
import requests
from click import secho
from django.core.files.images import ImageFile

from apps.accounts.models import UserProfile
from apps.accounts.services.user_profile_state_synchronizer import synchronizer


def load_picture(up):
    r = requests.get(f"https://fiesta.esncz.org/images/avatar/{up.avatar_slug}.jpg")

    up.picture = (
        ImageFile(
            BytesIO(r.content),
            name="image.jpg",
        )
        if r.status_code == 200
        else None
    )
    if up.picture:
        up.save(update_fields=["picture"])
        secho(f"Avatar for {up.user} loaded", fg="green")


@click.command()
def load_legacy_avatars():
    with synchronizer.without_profile_revalidation(), ProcessPoolExecutor(max_workers=64) as executor:
        executor.map(load_picture, UserProfile.objects.exclude(avatar_slug=""))
