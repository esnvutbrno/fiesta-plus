from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.universities.models.managers import FacultyManager
from apps.utils.models import BaseTimestampedModel


class Faculty(BaseTimestampedModel):
    name = models.CharField(
        max_length=128,
        verbose_name=_("name of faculty"),
        help_text=_("full name of faculty (w/o university)"),
    )
    abbr = models.SlugField(
        max_length=16,
        allow_unicode=True,
        verbose_name=_("abbreviation of faculty name"),
    )

    university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("related university"),
        db_index=True,
    )

    objects = FacultyManager()

    class Meta:
        verbose_name = _("faculty")
        verbose_name_plural = _("Faculties")
        ordering = ("university", "name")

    def __str__(self):
        return f"{self.university.abbr} {self.abbr}"


__all__ = ["Faculty"]
