from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class AccountsConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.accounts"

    configuration_model = "accounts.AccountsConfiguration"

    verbose_name = _("Users")

    membership_not_required_urls = ("profile-finish",)


__all__ = ["AccountsConfig"]
