from __future__ import annotations

from typing import TYPE_CHECKING

from django import forms
from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm
from apps.notifications.models import SectionNotificationPreferences

if TYPE_CHECKING:
    from apps.accounts.models import UserProfile
    from apps.sections.models import SectionMembership


class NotificationPreferencesForm(BaseModelForm):
    submit_text = _("Save preferences")
    email_notifications_enabled = forms.BooleanField(
        required=False,
        label=_("Enable email notifications"),
        help_text=_("Uncheck to disable all email notifications from fiesta.plus"),
    )

    class Meta:
        model = SectionNotificationPreferences
        fields = ["notify_on_match", "notify_on_new_member_waiting"]

    def __init__(
        self,
        *args: object,
        membership: SectionMembership | None = None,
        user_profile: UserProfile | None = None,
        **kwargs: object,
    ) -> None:
        self.user_profile = user_profile
        super().__init__(*args, **kwargs)
        if self.user_profile:
            self.fields["email_notifications_enabled"].initial = self.user_profile.email_notifications_enabled
        # Only editors and admins should see the "new member waiting" toggle
        if membership is None or not membership.is_privileged:
            self.fields.pop("notify_on_new_member_waiting", None)

    def save(self, commit: bool = True) -> SectionNotificationPreferences:
        instance = super().save(commit=commit)
        if self.user_profile:
            self.user_profile.email_notifications_enabled = self.cleaned_data["email_notifications_enabled"]
            self.user_profile.save(update_fields=["email_notifications_enabled"])
        return instance
