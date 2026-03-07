from __future__ import annotations

from typing import TYPE_CHECKING

from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.notifications.models import ScheduledNotification, SectionNotificationPreferences

if TYPE_CHECKING:
    from django.db.models import QuerySet
    from django.http import HttpRequest


@admin.register(SectionNotificationPreferences)
class SectionNotificationPreferencesAdmin(admin.ModelAdmin):
    list_display = ["user", "section", "notify_on_match", "notify_on_new_member_waiting", "created"]
    list_filter = ["section", "notify_on_match", "notify_on_new_member_waiting"]
    # user is FK → accounts.User
    search_fields = ["user__email", "user__first_name", "user__last_name", "section__name"]
    readonly_fields = ["created", "modified"]


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    list_display = ["kind", "recipient", "section", "send_after", "sent_at", "cancelled_at", "created"]
    list_filter = ["kind", "section"]
    # recipient is FK to accounts.User
    search_fields = ["recipient__email", "recipient__first_name", "recipient__last_name"]
    readonly_fields = ["created", "modified", "content_type", "object_id", "content_object"]
    date_hierarchy = "send_after"
    actions = ["mark_as_sent", "cancel_notifications"]

    def get_queryset(self, request: HttpRequest) -> QuerySet[ScheduledNotification]:
        return super().get_queryset(request).select_related("recipient", "section", "content_type")

    @admin.action(description=_("Send now (bypass send_after)"))
    def mark_as_sent(self, request: HttpRequest, queryset: QuerySet[ScheduledNotification]) -> None:
        updated = queryset.filter(sent_at__isnull=True, cancelled_at__isnull=True).update(send_after=timezone.now())
        self.message_user(request, _("Scheduled %s notification(s) to send immediately.") % updated)

    @admin.action(description=_("Cancel selected notifications"))
    def cancel_notifications(self, request: HttpRequest, queryset: QuerySet[ScheduledNotification]) -> None:
        count = 0
        for notification in queryset.filter(sent_at__isnull=True, cancelled_at__isnull=True):
            notification.cancel()
            notification.save(update_fields=["cancelled_at", "modified"])
            count += 1
        self.message_user(request, _("Cancelled %s notification(s).") % count)
