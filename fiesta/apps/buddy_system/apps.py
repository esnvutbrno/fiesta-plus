from django.utils.translation import gettext_lazy as _

from apps.plugins.plugin import PluginAppConfig


class BuddySystemConfig(PluginAppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.buddy_system"
    title = _("Buddy System")

    configuration_model = "buddy_system.BuddySystemConfiguration"

    login_not_required_urls = (
        "wanna-buddy",
        "sign-up-before-request",
    )

    membership_not_required_urls = ("new-request",)


__all__ = ["BuddySystemConfig"]
