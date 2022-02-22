from django.urls import path

from .views import EsncardsIndexView
from .views.application import ApplicationCreateView, ApplicationDetailView

urlpatterns = [
    path("create", ApplicationCreateView.as_view(), name="application_create_form"),
    path(
        "detail/<uuid:pk>", ApplicationDetailView.as_view(), name="application_detail"
    ),
    path("", EsncardsIndexView.as_view()),
]
