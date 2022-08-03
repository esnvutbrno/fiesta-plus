# https://github.com/jazzband/django-configurations/issues/147#issuecomment-300576651
from configurations import importer

from .checks import *  # noqa

importer.install(check_options=True)
