from __future__ import annotations

from django.urls import path

from .views import EventsIndexView

# Define your urls here
urlpatterns = [path("", EventsIndexView.as_view())]
