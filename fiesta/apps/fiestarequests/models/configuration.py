from django.db import models

from apps.fiestarequests.matching_policy import MatchingPoliciesRegister
from apps.plugins.models import BasePluginConfiguration


class BaseRequestSystemConfiguration(BasePluginConfiguration):
    display_issuer_picture = models.BooleanField(default=False)
    display_issuer_gender = models.BooleanField(default=False)
    display_issuer_country = models.BooleanField(default=False)
    display_issuer_university = models.BooleanField(default=False)
    display_issuer_faculty = models.BooleanField(default=False)
    display_request_creation_date = models.BooleanField(default=True)

    rolling_limit = models.PositiveSmallIntegerField(default=0)

    matching_policy = models.CharField(
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
        abstract = True
