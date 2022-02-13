from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class AccountsConfiguration(BasePluginConfiguration):
    required_nationality = models.BooleanField(
        verbose_name=_("required nationality"),
        default=None,
        null=True,
        blank=True,
        help_text=_(
            "Flag if nationality is needed to fill in user profile: "
            "True=is required, False=is optional, None=not available"
        ),
    )

    class Meta:
        verbose_name = _("accounts configuration")
        verbose_name_plural = _("accounts configurations")


__all__ = ["AccountsConfiguration"]
