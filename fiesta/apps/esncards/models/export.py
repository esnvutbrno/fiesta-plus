from __future__ import annotations

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class Export(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("section"),
        db_index=True,
    )

    class State(TextChoices):
        CREATED = "created", _("Created")
        MATERIALS_GENERATED = "prepared", _("Prepared")
        EXPORTED = "exported", _("Exported")

    state = models.CharField(
        verbose_name=_("state"),
        max_length=20,
        choices=State.choices,
        default=State.CREATED,
    )
