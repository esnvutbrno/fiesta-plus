from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class BaseRequestSystemConfiguration(BasePluginConfiguration):
    display_issuer_picture = models.BooleanField(default=False)
    display_issuer_gender = models.BooleanField(default=False)
    display_issuer_country = models.BooleanField(default=False)
    display_issuer_university = models.BooleanField(default=False)
    display_issuer_faculty = models.BooleanField(default=False)
    display_request_creation_date = models.BooleanField(default=True)

    rolling_limit = models.PositiveSmallIntegerField(default=0)

    enable_note_from_matcher = models.BooleanField(
        default=True,
        help_text=_("Allows matcher to reply with custom notes to the request issuer"),
    )

    class Meta:
        abstract = True
