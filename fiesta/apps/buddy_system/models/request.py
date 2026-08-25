from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db.models import BooleanField, CharField
from django.utils.translation import gettext_lazy as _

from apps.accounts.conf import INTERESTS_CHOICES
from apps.accounts.models import UserProfile
from apps.fiestarequests.models import base_request_model_factory
from apps.utils.models.fields import ArrayFieldWithDisplayableChoices

BaseRequestForBuddySystem, BaseRequestMatchForBuddySystem = base_request_model_factory(
    final_request_model_name="buddy_system.BuddyRequest",
    related_base="buddy_system",
    url_namespace="buddy_system",
)


class BuddyRequest(BaseRequestForBuddySystem):
    interests = ArrayFieldWithDisplayableChoices(
        base_field=CharField(
            choices=INTERESTS_CHOICES,
            max_length=24,
            # inner field could be empty (default to remove empty option in .choices)
            default=None,
        ),
        verbose_name=_("issuer interests"),
        default=list,  # as callable to not share instance,
        blank=True,
    )

    same_gender_only = BooleanField(
        default=False,
        verbose_name=_("only same-gender buddy"),
        help_text=_(
            "Require that only a buddy of the same gender as you can match with you. "
            "Available only if your profile gender is set to male or female."
        ),
    )
    # cloned from issuer's profile at creation time, mirroring issuer_faculty above, so the
    # same-gender constraint stays stable even if the issuer later changes their profile gender
    issuer_gender = CharField(
        choices=UserProfile.Gender.choices,
        blank=True,
        max_length=16,
        verbose_name=_("issuer's gender"),
    )

    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request")
        verbose_name_plural = _("buddy requests")


class BuddyRequestMatch(BaseRequestMatchForBuddySystem):
    class Meta(BaseRequestForBuddySystem.Meta):
        verbose_name = _("buddy request match")
        verbose_name_plural = _("buddy request matches")

    def clean(self):
        super().clean()

        if not self.request_id or not self.matcher_id or not self.request.same_gender_only:
            return

        from apps.buddy_system.apps import BuddySystemConfig
        from apps.plugins.models import Plugin
        from apps.plugins.utils import all_plugins_mapped_to_class

        buddy_system_app = all_plugins_mapped_to_class().get(BuddySystemConfig)
        if not buddy_system_app:
            return

        try:
            plugin = self.request.responsible_section.plugins.get(
                app_label=buddy_system_app.label,
            )
        except Plugin.DoesNotExist:
            return

        configuration = plugin.configuration
        if not configuration or not configuration.enable_same_gender_matching:
            return

        if self.request.issuer_gender not in (UserProfile.Gender.MALE, UserProfile.Gender.FEMALE):
            # constraint is only meaningful for male/female issuers; treat it as inactive otherwise
            return

        matcher_profile = self.matcher.profile_or_none
        if not matcher_profile or matcher_profile.gender != self.request.issuer_gender:
            raise ValidationError(_("This request can only be matched with a buddy of the same gender."))
