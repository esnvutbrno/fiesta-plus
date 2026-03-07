from __future__ import annotations

from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic.edit import UpdateView

from apps.buddy_system.apps import BuddySystemConfig
from apps.notifications.forms import NotificationPreferencesForm
from apps.notifications.models import SectionNotificationPreferences
from apps.pickup_system.apps import PickupSystemConfig
from apps.plugins.views.mixins import CheckEnabledPluginsViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet


class NotificationPreferencesView(
    LoginRequiredMixin,
    EnsureInSectionSpaceViewMixin,
    CheckEnabledPluginsViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    model = SectionNotificationPreferences
    form_class = NotificationPreferencesForm
    template_name = "notifications/preferences.html"

    success_message = _("Notification preferences saved.")

    def get_success_url(self) -> str:
        return self.request.path

    def get_object(self, queryset: QuerySet | None = None) -> SectionNotificationPreferences:
        obj, _ = SectionNotificationPreferences.objects.get_or_create(
            user=self.request.user,
            section=self.request.in_space_of_section,
            defaults={
                "notify_on_match": True,
                "notify_on_new_member_waiting": True,
            },
        )
        return obj

    def get_form_kwargs(self) -> dict[str, Any]:
        kwargs = super().get_form_kwargs()
        kwargs["membership"] = getattr(self.request, "membership", None)
        kwargs["user_profile"] = getattr(self.request.user, "profile", None)
        return kwargs

    def get_form(self, form_class: type[NotificationPreferencesForm] | None = None) -> NotificationPreferencesForm:
        form = super().get_form(form_class)
        # Hide match notification toggle when neither buddy_system nor pickup_system is enabled
        if not self._is_plugin_enabled_for_user(BuddySystemConfig) and not self._is_plugin_enabled_for_user(
            PickupSystemConfig
        ):
            form.fields.pop("notify_on_match", None)
        return form
