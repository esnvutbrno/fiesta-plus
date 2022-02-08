from django.urls import path

from .views import EsncardsIndexView
from .views.application import ApplicationCreateView, ApplicationDetailView

urlpatterns = [
    path("create", ApplicationCreateView.as_view(), name="create-application-form"),
    path(
        "detail/<uuid:pk>", ApplicationDetailView.as_view(), name="detail-application"
    ),
    path("", EsncardsIndexView.as_view()),
]
