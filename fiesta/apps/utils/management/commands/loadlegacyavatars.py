from __future__ import annotations

from io import BytesIO

import djclick as click
import requests
from click import secho
from django.core.files.images import ImageFile

from apps.accounts.models import UserProfile


@click.command()
def load_legacy_avatars():
    for up in UserProfile.objects.filter(picture="").exclude(avatar_slug=""):
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
