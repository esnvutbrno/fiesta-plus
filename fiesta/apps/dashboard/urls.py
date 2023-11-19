from __future__ import annotations

from django.urls import path

from .views import DashboardIndexView

urlpatterns = [path("", DashboardIndexView.as_view(), name="index")]
