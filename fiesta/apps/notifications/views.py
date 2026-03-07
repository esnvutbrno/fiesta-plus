from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.signing import BadSignature, SignatureExpired
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import UpdateView

from apps.accounts.models import UserProfile
from apps.buddy_system.apps import BuddySystemConfig
from apps.notifications.forms import NotificationPreferencesForm
from apps.notifications.models import NotificationKind, SectionNotificationPreferences
from apps.notifications.services.unsubscribe import verify_unsubscribe_token
from apps.pickup_system.apps import PickupSystemConfig
from apps.plugins.views.mixins import CheckEnabledPluginsViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin

if TYPE_CHECKING:
    from django.db.models import QuerySet

logger = logging.getLogger(__name__)


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


@method_decorator(csrf_exempt, name="dispatch")
class UnsubscribeView(View):
    template_name = "notifications/unsubscribe.html"

    def get(self, request: object, token: str) -> HttpResponse:
        try:
            user_profile, action = self._resolve_token(token)
        except UserProfile.DoesNotExist:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link is invalid.")},
                status=400,
            )
        except SignatureExpired:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link has expired.")},
                status=400,
            )
        except BadSignature:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link is invalid.")},
                status=400,
            )

        return render(
            request,
            self.template_name,
            {
                "action": action,
                "action_description": self._action_description(action),
                "email": user_profile.user.email,
            },
        )

    def post(self, request: object, token: str) -> HttpResponse:
        try:
            user_profile, action = self._resolve_token(token)
            self._unsubscribe(user_profile=user_profile, action=action)
        except UserProfile.DoesNotExist:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link is invalid.")},
                status=200,
            )
        except SignatureExpired:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link has expired.")},
                status=200,
            )
        except BadSignature:
            return render(
                request,
                self.template_name,
                {"error": _("This unsubscribe link is invalid.")},
                status=200,
            )

        return render(
            request,
            self.template_name,
            {
                "success": True,
                "action": action,
                "action_description": self._action_description(action),
            },
        )

    def _resolve_token(self, token: str) -> tuple[UserProfile, str]:
        user_id, action = verify_unsubscribe_token(token)
        return UserProfile.objects.select_related("user").get(pk=user_id), action

    def _unsubscribe(self, *, user_profile: UserProfile, action: str) -> None:
        if action == "global":
            if user_profile.email_notifications_enabled:
                user_profile.email_notifications_enabled = False
                user_profile.save(update_fields=["email_notifications_enabled", "modified"])
            return

        if action in {NotificationKind.BUDDY_MATCHED_ISSUER, NotificationKind.PICKUP_MATCHED_ISSUER}:
            SectionNotificationPreferences.objects.filter(user=user_profile).update(notify_on_match=False)
            return

        if action == NotificationKind.MEMBER_WAITING_DIGEST:
            SectionNotificationPreferences.objects.filter(user=user_profile).update(notify_on_new_member_waiting=False)
            return

        logger.warning("Unsupported unsubscribe action %r for user_profile=%s", action, user_profile.pk)

    def _action_description(self, action: str) -> str:
        if action == "global":
            return _("all email notifications")

        if action in {NotificationKind.BUDDY_MATCHED_ISSUER, NotificationKind.PICKUP_MATCHED_ISSUER}:
            return _("match notification emails")

        if action == NotificationKind.MEMBER_WAITING_DIGEST:
            return _("new member waiting digest emails")

        return _("selected email notifications")
