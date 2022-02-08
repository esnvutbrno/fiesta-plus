from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class AccountsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    configuration_model = "accounts.AccountsConfiguration"

    title = _("Users")


__all__ = ["AccountsConfig"]
