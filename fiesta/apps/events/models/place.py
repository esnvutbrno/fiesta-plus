from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _
import re

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
        blank=True,
        default="",

    )

    link = models.CharField(
        max_length=256,
        verbose_name=_("webpage link"),
        help_text=_("Link to the place"),
        blank=True,
        default="",
    )

    map_link = models.CharField(
        max_length=256,
        verbose_name=_("map link"),
        help_text=_("Link to google maps in format google.com/maps/place/<place>/\@<coordinates>/data"),
        blank=True,
        default="",
    )
    
    longitude = models.FloatField(
        verbose_name=_("longitude"),
        blank=True,
        default=0.0
    )
    
    latitude = models.FloatField(
        verbose_name=_("latitude"),
        blank=True,
        default=0.0
    )

    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.CASCADE,
        related_name="places",
        verbose_name=_("ESN section"),
        db_index=True,
    )

    def __str__(self):
        return self.name
    
    def set_coordinates_from_url(self, url):
        match = re.search(r'([-\d.]+),([-\d.]+)', url)
        if match:
            self.latitude, self.longitude = map(float, match.groups())
            return True
        return False

    class Meta:
        verbose_name = _("place")
        verbose_name_plural = _("places")
        unique_together = (("section", "name"),)


__all__ = ["Place"]
