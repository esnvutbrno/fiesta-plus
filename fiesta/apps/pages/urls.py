from __future__ import annotations

from django.urls import path

from .views import PagesIndexView

# Define your urls here
urlpatterns = [path("", PagesIndexView.as_view())]
