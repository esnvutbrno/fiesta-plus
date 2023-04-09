from __future__ import annotations

from django.urls import path

from .views import DashboardIndexView

# Define your urls here
urlpatterns = [path("", DashboardIndexView.as_view())]
