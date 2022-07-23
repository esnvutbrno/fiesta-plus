from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel
from apps.utils.models.validators import validate_plain_slug_lowercase


class Section(BaseTimestampedModel):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_("name"),
        help_text=_("Full name of section, e.g. ESN VUT Brno"),
    )
    country = CountryField(
        verbose_name=_("country"),
    )

    universities = models.ManyToManyField(
        "universities.University",
        through="sections.SectionUniversity",
        verbose_name=_("universities"),
        help_text=_("Universities, for whose this section offers services."),
    )

    code = models.SlugField(
        verbose_name=_("code"),
        help_text=_("Official code used in ESN world, especially in ESN Accounts database."),
        # TODO: remove blankness after proper migration from ESN accounts
        null=True,
        blank=True,
        unique=True,
    )

    space_slug = models.SlugField(
        verbose_name=_("space slug"),
        help_text=_("Slug used for defining section spaces as URL subdomains."),
        unique=True,
        validators=[validate_plain_slug_lowercase],
    )

    class Meta:
        verbose_name = _("ESN section")
        verbose_name_plural = _("ESN sections")
        ordering = ("country", "name")

    def __str__(self):
        return self.name


class SectionUniversity(BaseTimestampedModel):
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("ESN section"),
        db_index=False,
    )
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.CASCADE,
        verbose_name=_("university"),
        db_index=False,
    )

    class Meta:
        verbose_name = _("Section university")
        verbose_name_plural = _("Section universities")
        unique_together = (("section", "university"),)

    def __str__(self):
        return f"{self.section} - {self.university}"


__all__ = ["Section", "SectionUniversity"]
