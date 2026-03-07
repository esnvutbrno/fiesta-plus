from __future__ import annotations

from django.urls import path

from apps.notifications.views import NotificationPreferencesView, UnsubscribeView

app_name = "notifications"

urlpatterns = [
    path("preferences/", NotificationPreferencesView.as_view(), name="preferences"),
    path("unsubscribe/<path:token>/", UnsubscribeView.as_view(), name="unsubscribe"),
]
