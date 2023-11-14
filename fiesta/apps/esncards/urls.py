from __future__ import annotations

from django.urls import path

from .views import EsncardIndexView
from .views.application import ApplicationCreateView, ApplicationDetailView
from .views.applications import ApplicationsView

urlpatterns = [
    path("create", ApplicationCreateView.as_view(), name="application_create_form"),
    path("detail/<uuid:pk>", ApplicationDetailView.as_view(), name="application_detail"),
    path("list", ApplicationsView.as_view(), name="applications"),
    path("", EsncardIndexView.as_view()),
]
