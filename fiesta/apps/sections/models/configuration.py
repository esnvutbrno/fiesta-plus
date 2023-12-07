from __future__ import annotations

from django.db.models import BooleanField
from django.utils.translation import gettext_lazy as _
from django_lifecycle import AFTER_SAVE, hook

from apps.plugins.models import BasePluginConfiguration

FLAG_HELP_TEXT = _(
    "Flag if field is needed to fill in user profile: "
    "Yes=field is required, No=field is optional, Unknown=field is not available"
)


class SectionsConfiguration(BasePluginConfiguration):
    required_university = BooleanField(
        verbose_name=_("required university"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_faculty = BooleanField(
        verbose_name=_("required faculty"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_nationality = BooleanField(
        verbose_name=_("required nationality"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_gender = BooleanField(
        verbose_name=_("required gender"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_picture = BooleanField(
        verbose_name=_("required profile picture"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_phone_number = BooleanField(
        verbose_name=_("required phone number"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )
    required_interests = BooleanField(
        verbose_name=_("required interests"),
        default=None,
        null=True,
        blank=True,
        help_text=FLAG_HELP_TEXT,
    )

    auto_approved_membership_for_international = BooleanField(
        verbose_name=_("auto approved membership for international"),
        default=True,
        help_text=_(
            "Decides, whenever is membership requested by user automatically approved for international users (e.g."
            " during registration process or requested by membership form)."
        ),
    )

    class Meta:
        verbose_name = _("section configuration")
        verbose_name_plural = _("section configurations")

    @hook(AFTER_SAVE)
    def on_save(self):
        from apps.accounts.services.user_profile_state_synchronizer import synchronizer

        synchronizer.on_accounts_configuration_update(conf=self)


__all__ = ["SectionsConfiguration"]
