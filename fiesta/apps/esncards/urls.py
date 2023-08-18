from __future__ import annotations

from django.urls import path

from .views import EsncardsIndexView
from .views.application import ApplicationCreateView, ApplicationDetailView
from .views.applications import ApplicationsView
from .views.exports import NewExportView

urlpatterns = [
    path("create", ApplicationCreateView.as_view(), name="application_create_form"),
    path("detail/<uuid:pk>", ApplicationDetailView.as_view(), name="application_detail"),
    path("applications", ApplicationsView.as_view(), name="applications"),
    path("new-export/<str:applications>", NewExportView.as_view(), name="new-export"),
    path("", EsncardsIndexView.as_view()),
]
