from __future__ import annotations

import typing
import uuid

from django.db import models
from django.db.models import TextChoices
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django_lifecycle import LifecycleModelMixin

from apps.fiestarequests.models.managers.request import BaseRequestManager, BaseRequestMatchManager
from apps.sections.models import Section
from apps.utils.models import BaseTimestampedModel

if typing.TYPE_CHECKING:
    from apps.accounts.models import User


class BaseRequestProtocol(typing.Protocol):
    pk: uuid.UUID

    class State(TextChoices):
        CREATED = "created", _("Created")
        MATCHED = "matched", _("Matched")

        CANCELLED = "cancelled", _("Cancelled")

    state: models.CharField | State
    issuer: models.ForeignKey | User
    responsible_section: models.ForeignKey | Section
    note: models.TextField | str
    match: BaseRequestMatchProtocol | models.Model

    objects: BaseRequestManager


class BaseRequestMatchProtocol(typing.Protocol):
    request: models.ForeignKey | BaseRequestProtocol
    matcher: models.ForeignKey | User
    note: models.TextField | str

    objects: BaseRequestMatchManager


def base_request_model_factory(
    related_base: str,
    final_request_model_name: str,
    url_namespace: str,
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
        issuer: User = models.ForeignKey(
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

        # fields cloned from issuer/issuer's profile to have consistency over time
        issuer_faculty = models.ForeignKey(
            "universities.Faculty",
            related_name=f"{related_base}_issued_requests",
            on_delete=models.RESTRICT,
            verbose_name=_("issuer's faculty"),
            db_index=True,
        )

        @property
        def issuer_picture_url(self):
            return (
                reverse(f"{url_namespace}:serve-issuer-profile-picture", args=(self.issuer.profile_or_none.picture,))
                if self.issuer.profile_or_none
                else None
            )

        def __str__(self):
            return f"{self.issuer}: {self.get_state_display()}"

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

        matcher: User = models.ForeignKey(
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

        # fields cloned from matcher/matcher's profile to have consistency over time
        matcher_faculty = models.ForeignKey(
            "universities.Faculty",
            related_name=f"{related_base}_request_matches",
            on_delete=models.RESTRICT,
            verbose_name=_("matcher's faculty"),
            db_index=True,
        )

        @property
        def matcher_picture_url(self):
            return (
                reverse(f"{url_namespace}:serve-matcher-profile-picture", args=(self.matcher.profile_or_none.picture,))
                if self.matcher.profile_or_none
                else None
            )

        def __str__(self):
            return f"{self.request} - {self.matcher}"

    return BaseRequest, BaseRequestMatch
