# https://github.com/jazzband/django-configurations/issues/147#issuecomment-300576651
from __future__ import annotations

from configurations import importer

from .checks import *  # noqa

importer.install(check_options=True)
