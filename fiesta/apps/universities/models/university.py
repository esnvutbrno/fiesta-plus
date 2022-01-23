from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel


class University(BaseTimestampedModel):
    name = models.CharField(max_length=128, verbose_name=_("full name of university"))
    abbr = models.SlugField(
        max_length=16,
        allow_unicode=True,
        verbose_name=_("abbreviation of university name"),
    )

    country = CountryField(verbose_name=_("country of university"))

    class Meta:
        verbose_name = _("university")
        verbose_name_plural = _("universities")
        ordering = ["name"]

    def __str__(self):
        return self.name


#
# class Section(BaseTimestampedModel):
#     name = models.CharField(
#         max_length=64,
#         unique=True,
#     )
#
#     general_email = models.EmailField(
#         blank=True,
#         null=True,
#     )
#
#     founding = models.DateField()


__all__ = ["University"]
