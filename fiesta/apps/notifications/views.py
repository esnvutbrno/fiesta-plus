from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import UpdateView

from apps.notifications.forms import NotificationPreferencesForm
from apps.notifications.models import SectionNotificationPreferences
from apps.plugins.middleware.plugin import HttpRequest


class NotificationPreferencesView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = SectionNotificationPreferences
    form_class = NotificationPreferencesForm
    template_name = "notifications/preferences.html"

    request: HttpRequest
    success_message = _("Notification preferences saved.")

    def get_success_url(self) -> str:
        return self.request.path

    def get_object(self, queryset=None) -> SectionNotificationPreferences:
        obj, _ = SectionNotificationPreferences.objects.get_or_create(
            user=self.request.user.profile,
            section=self.request.in_space_of_section,
            defaults={
                "notify_on_match": True,
                "notify_on_new_member_waiting": True,
            },
        )
        return obj

    def get_form_kwargs(self) -> dict:
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = getattr(self.request, "membership", None)
        return kwargs
