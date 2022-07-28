from django.db import models
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, hook

from apps.plugins.models import BasePluginConfiguration

FLAG_HELP_TEXT = _(
    "Flag if field is needed to fill in user profile: "
    "True=is required, False=is optional, None=not available"
)


class AccountsConfiguration(BasePluginConfiguration):
    required_nationality = models.BooleanField(
        verbose_name=_("required nationality"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_gender = models.BooleanField(
        verbose_name=_("required gender"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_picture = models.BooleanField(
        verbose_name=_("required profile picture"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )

    class Meta:
        verbose_name = _("accounts configuration")
        verbose_name_plural = _("accounts configurations")

    @hook(AFTER_SAVE)
    def on_save(self):
        from apps.accounts.services import UserProfileStateSynchronizer

        UserProfileStateSynchronizer.on_accounts_configuration_update(conf=self)


__all__ = ["AccountsConfiguration"]
