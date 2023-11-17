from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.matching_policy import MatchingPoliciesRegister
from apps.fiestarequests.models import BaseRequestSystemConfiguration


class BuddySystemConfiguration(BaseRequestSystemConfiguration):
    matching_policy = models.CharField(
        verbose_name=_("matching policy"),
        default=MatchingPoliciesRegister.DEFAULT_POLICY.id,
        choices=MatchingPoliciesRegister.CHOICES,
        max_length=32,
        help_text=MatchingPoliciesRegister.DESCRIPTION,
    )

    @property
    def matching_policy_instance(self):
        # TODO: pass configuration?
        return MatchingPoliciesRegister.get_policy_by_id(self.matching_policy)

    class Meta:
        verbose_name = _("buddy system configuration")
        verbose_name_plural = _("buddy system configurations")


__all__ = ["BuddySystemConfiguration"]
