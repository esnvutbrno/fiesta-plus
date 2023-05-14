from __future__ import annotations

from io import BytesIO

import djclick as click
import requests
from click import secho
from django.core.files.images import ImageFile

from apps.accounts.models import UserProfile


@click.command()
def seed():
    for up in UserProfile.objects.all():
        picture = requests.get(f"https://i.pravatar.cc/150?u={up.user_id}")
        f = BytesIO(picture.content)
        up.picture = ImageFile(f, "picture.jpg")
        up.save()
        secho(up)
