from django.utils.translation import gettext_lazy as _

from apps.plugins.models import BasePluginConfiguration


class AccountsConfiguration(BasePluginConfiguration):
    class Meta:
        verbose_name = _("accounts configuration")
        verbose_name_plural = _("accounts configurations")


__all__ = ["AccountsConfiguration"]
