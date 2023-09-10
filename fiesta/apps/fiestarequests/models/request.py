from __future__ import annotations

import datetime
import typing

from django.db import models
from django.db.models import TextChoices
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django_lifecycle import BEFORE_SAVE, LifecycleModelMixin, hook

from apps.accounts.models import User
from apps.fiestarequests.models.managers.request import BaseRequestManager
from apps.sections.models import Section
from apps.utils.models import BaseTimestampedModel


class BaseRequestProtocol(typing.Protocol):
    class State(TextChoices):
        CREATED = "created", _("Created")
        MATCHED = "matched", _("Matched")

        CANCELLED = "cancelled", _("Cancelled")

    state: models.CharField | State
    issuer: models.ForeignKey | User
    responsible_section: models.ForeignKey | Section
    matched_by: models.ForeignKey | User
    matched_at: models.DateTimeField | datetime.datetime
    description: models.TextField | str

    objects: BaseRequestManager


def base_request_model_factory(related_base: str):
    """
    Creates a base model for requests-like models.
    """

    class BaseRequest(LifecycleModelMixin, BaseTimestampedModel):
        class Meta(BaseTimestampedModel.Meta):
            abstract = True
            ordering = ("-created",)

        State = BaseRequestProtocol.State

        objects = BaseRequestManager()

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

        issuer_note = models.TextField(
            verbose_name=_("text from issuer"),
        )

        matcher_note = models.TextField(
            verbose_name=_("text from matcher"),
        )

        @hook(BEFORE_SAVE, when="matched_by", was=None, is_not=None)
        def set_matched_at(self):
            self.matched_at = now()

    return BaseRequest
