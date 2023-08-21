from __future__ import annotations

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class Export(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("section"),
        related_name="esncard_exports",
        db_index=True,
    )

    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.RESTRICT,
        verbose_name=_("created by"),
        related_name="esncard_exports",
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
