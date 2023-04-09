from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import TypedDict

from django.contrib.auth import get_user_model
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.db.models import TextChoices
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from django_lifecycle import BEFORE_CREATE, BEFORE_SAVE, LifecycleModelMixin, hook

from apps.files.storage import NamespacedFilesStorage
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.models import BaseTimestampedModel
from apps.utils.models.query import get_single_object_or_none

logger = logging.getLogger(__name__)


def has_permission_to_view_holder_photo(request: HttpRequest, name: str) -> bool:
    if not request.membership:
        return False

    application: ESNcardApplication = get_single_object_or_none(ESNcardApplication, holder_photo=name)

    if not application:
        logger.warning("Photo exists %s in storage, but no related application.", name)
        return False

    if application.section != request.membership.section:
        return False

    if request.membership.is_privileged:
        return True

    return application.user == request.user


esncard_application_picture_storage = NamespacedFilesStorage(
    "esncard-application-picture",
    has_permission=has_permission_to_view_holder_photo,
)


class ESNcardApplication(LifecycleModelMixin, BaseTimestampedModel):
    # copied from user
    first_name = models.CharField(
        verbose_name=_("first name"),
        max_length=150,
    )
    last_name = models.CharField(verbose_name=_("last name"), max_length=150)
    nationality = CountryField(verbose_name=_("nationality"))
    university = models.ForeignKey(
        "universities.University",
        on_delete=models.RESTRICT,
        verbose_name=_("university"),
        db_index=True,
    )

    # filled by user
    birth_date = models.DateField(verbose_name=_("birth date"))

    holder_photo = models.ImageField(
        verbose_name=_("holder photo"),
        upload_to=esncard_application_picture_storage.upload_to,
        storage=esncard_application_picture_storage,
        help_text=_("Front passport-sized photo is needed."),
    )

    # related to request
    section = models.ForeignKey(
        "sections.Section",
        on_delete=models.RESTRICT,
        verbose_name=_("section"),
        db_index=True,
    )
    user = models.ForeignKey(
        "accounts.User",
        related_name="esncard_applications",
        on_delete=models.RESTRICT,
        verbose_name=_("issuer"),
        db_index=True,
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
        verbose_name=_("state"),
    )

    history: list[HistoryRecord] = models.JSONField(
        default=list,
        encoder=DjangoJSONEncoder,
    )

    class HistoryRecord(TypedDict):
        timestamp: datetime
        initial_state: ESNcardApplication.State | str
        final_state: ESNcardApplication.State | str
        user_id: int | None = None

        @property
        def user(self):
            return get_single_object_or_none(get_user_model(), pk=self.user_id)

    class Meta:
        verbose_name = _("ESNcard application")
        verbose_name_plural = _("ESNcard applications")

    @property
    def holder_full_name(self):
        return f"{self.first_name} {self.last_name}"

    @hook(BEFORE_SAVE, when="state", has_changed=True)
    @hook(BEFORE_CREATE)
    def on_state_change(self):
        self.history.append(
            self.HistoryRecord(
                timestamp=timezone.now(),
                initial_state=self.initial_value("state"),
                final_state=self.state,
            )
        )

    def __str__(self):
        return _("ESNcard Application: {}").format(self.get_state_display())

    @property
    def to_be_ready_at(self):
        return self.created + timedelta(days=10)


__all__ = ["ESNcardApplication"]
