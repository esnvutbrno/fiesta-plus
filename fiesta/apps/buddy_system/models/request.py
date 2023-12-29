from __future__ import annotations

from django.db.models import CharField
from django.utils.translation import gettext_lazy as _

from apps.accounts.conf import INTERESTS_CHOICES
from apps.fiestarequests.models import base_request_model_factory
from apps.utils.models.fields import ArrayFieldWithDisplayableChoices

BaseRequestForBuddySystem, BaseRequestMatchForBuddySystem = base_request_model_factory(
    final_request_model_name="buddy_system.BuddyRequest",
    related_base="buddy_system",
    url_namespace="buddy_system",
)


class BuddyRequest(BaseRequestForBuddySystem):
    interests = ArrayFieldWithDisplayableChoices(
        base_field=CharField(
            choices=INTERESTS_CHOICES,
            max_length=24,
            # inner field could be empty (default to remove empty option in .choices)
            default=None,
        ),
        verbose_name=_("issuer interests"),
        default=list,  # as callable to not share instance,
        blank=True,
    )

    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request")
        verbose_name_plural = _("buddy requests")


class BuddyRequestMatch(BaseRequestMatchForBuddySystem):
    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request match")
        verbose_name_plural = _("buddy request matches")
