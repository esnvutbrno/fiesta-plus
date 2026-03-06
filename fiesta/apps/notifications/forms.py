from __future__ import annotations

from django.utils.translation import gettext_lazy as _

from apps.fiestaforms.forms import BaseModelForm
from apps.notifications.models import SectionNotificationPreferences


class NotificationPreferencesForm(BaseModelForm):
    submit_text = _("Save preferences")

    class Meta:
        model = SectionNotificationPreferences
        fields = ["notify_on_match", "notify_on_new_member_waiting"]

    def __init__(self, *args, membership=None, **kwargs):
        super().__init__(*args, **kwargs)
        # Only editors and admins should see the "new member waiting" toggle
        if membership is None or not membership.is_privileged:
            self.fields.pop("notify_on_new_member_waiting", None)
