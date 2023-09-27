from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseModel


class Place(BaseModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("name"),
        help_text=_("Name of the place"),
    )

    description = models.CharField(
        max_length=256,
        verbose_name=_("description"),
        help_text=_("Descriptions of the place or directions"),
        null=True,
        blank=True,
    )

    link = models.CharField(
        max_length=256,
        verbose_name=_("webpage link"),
        help_text=_("Link to the place"),
        null=True,
        blank=True,
    )

    map_link = models.CharField(
        max_length=256,
        verbose_name=_("map link"),
        help_text=_("Link to a position to the place on a map"),
        null=True,
        blank=True,
    )

    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        verbose_name=_("ESN section"),
        db_index=True,
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        unique_together = (("section", "name"),)

    # TODO nearest tram stop?

    def __str__(self):
        return self.name


__all__ = ["Place"]
