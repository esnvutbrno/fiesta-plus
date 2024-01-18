from __future__ import annotations

import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.matching_policy import BaseMatchingPolicy, MatchingPoliciesRegister
from apps.fiestarequests.models import BaseRequestSystemConfiguration


class BuddySystemConfiguration(BaseRequestSystemConfiguration):
    rolling_limit = models.PositiveSmallIntegerField(
        verbose_name=_("rolling limit"),
        default=0,
        help_text=_(
            "Number of requests a member can match in the time rolling window. "
            "Members with reached limit in specified time-window won't be able to "
            "match another buddy request. "
            "Set to 0 to disable limit."
        ),
    )
    rolling_limit_window = models.DurationField(
        verbose_name=_("rolling limit time window"),
        default=datetime.timedelta(weeks=4 * 3),  # 3 months
        help_text=_("Time window for the rolling limit. Use format DD HH:MM:SS."),
    )

    matching_policy = models.CharField(
        verbose_name=_("matching policy"),
        default=MatchingPoliciesRegister.DEFAULT_POLICY.id,
        choices=MatchingPoliciesRegister.CHOICES,
        max_length=32,
        help_text=MatchingPoliciesRegister.DESCRIPTION,
    )

    @property
    def matching_policy_instance(self) -> BaseMatchingPolicy:
        return MatchingPoliciesRegister.get_policy(self)

    class Meta:
        verbose_name = _("buddy system configuration")
        verbose_name_plural = _("buddy system configurations")


__all__ = ["BuddySystemConfiguration"]
