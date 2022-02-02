from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField

from apps.utils.models import BaseTimestampedModel


class ESNcardApplication(BaseTimestampedModel):
    # copied from user
    first_name = models.CharField(verbose_name=_("first name"), max_length=150)
    last_name = models.CharField(verbose_name=_("last name"), max_length=150)
    nationality = CountryField(verbose_name=_("nationality"))
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("university"),
    )

    # filled by user
    birth_date = models.DateField(verbose_name=_("birth date"))

    # related to request
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("section"),
    )
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.RESTRICT,
        verbose_name=_("issuer"),
    )

    class State(TextChoices):
        CREATED = "created", _("Created")
        ACCEPTED = "accepted", _("Accepted")
        READY_TO_PICKUP = "ready", _("Ready to pickup")
        ISSUED = "issued", _("Issued")

        DECLINED = "declined", _("Declined")
        CANCELLED = "cancelled", _("Cancelled")

    state = models.TextField(
        max_length=16,
        choices=State.choices,
        default=State.CREATED,
    )

    class Meta:
        verbose_name = _("ESNcard application")
        verbose_name_plural = _("ESNcard applications")


__all__ = ["ESNcardApplication"]
