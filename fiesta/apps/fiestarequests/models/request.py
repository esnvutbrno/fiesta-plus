from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

from apps.utils.models import BaseTimestampedModel


def base_request_model_factory(related_base: str):
    class BaseRequest(BaseTimestampedModel):
        class State(TextChoices):
            CREATED = "created", _("Created")
            MATCHED = "matched", _("Matched")

            CANCELLED = "cancelled", _("Cancelled")

        class Meta:
            abstract = True

        state = models.CharField(
            verbose_name=_("state"),
            choices=State.choices,
            default=State.CREATED,
            max_length=16,
        )
        issuer = models.ForeignKey(
            "accounts.User",
            related_name=f"{related_base}_issued_requests",
            on_delete=models.RESTRICT,
            verbose_name=_("issuer"),
            db_index=True,
        )
        responsible_section = models.ForeignKey(
            "sections.Section",
            related_name=f"{related_base}_requests",
            on_delete=models.RESTRICT,
            verbose_name=_("responsible section"),
            db_index=True,
        )
        matched_by = models.ForeignKey(
            "accounts.User",
            related_name=f"{related_base}_matched_requests",
            on_delete=models.RESTRICT,
            verbose_name=_("matched by"),
            db_index=True,
            null=True,
            blank=True,
        )
        matched_at = models.DateTimeField(
            verbose_name=_("matched at"),
            null=True,
            blank=True,
        )

    return BaseRequest
