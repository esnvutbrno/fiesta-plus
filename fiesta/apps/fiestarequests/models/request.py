from __future__ import annotations

import typing

from django.db import models
from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin

from apps.accounts.models import User
from apps.fiestarequests.models.managers.request import BaseRequestManager, BaseRequestMatchManager
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
    note: models.TextField | str

    objects: BaseRequestManager


class BaseRequestMatchProtocol(typing.Protocol):
    request: models.ForeignKey | BaseRequestProtocol
    matcher: models.ForeignKey | User
    note: models.TextField | str

    objects: BaseRequestMatchManager


def base_request_model_factory(
    related_base: str,
    final_request_model_name: str,
):
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

        note = models.TextField(
            verbose_name=_("text from issuer"),
        )

    class BaseRequestMatch(BaseTimestampedModel):
        class Meta(BaseTimestampedModel.Meta):
            abstract = True
            ordering = ("-created",)

        request = models.OneToOneField(
            final_request_model_name,
            related_name="match",
            on_delete=models.CASCADE,
            verbose_name=_("request"),
        )

        matcher = models.ForeignKey(
            "accounts.User",
            related_name=f"{related_base}_request_matches",
            on_delete=models.RESTRICT,
            verbose_name=_("matched by"),
            db_index=True,
        )

        note = models.TextField(
            verbose_name=_("text from matcher"),
            blank=True,
        )

    return BaseRequest, BaseRequestMatch
