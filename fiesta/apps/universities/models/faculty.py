from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


class Faculty(BaseTimestampedModel):
    name = models.CharField(max_length=128)
    abbreviation = models.SlugField(max_length=16)

    university = models.ForeignKey("universities.University", on_delete=models.RESTRICT)

    class Meta:
        verbose_name = _("faculty")
        verbose_name_plural = _("faculties")


__all__ = ["Faculty"]
