from __future__ import annotations

from django.urls import path

from .views import SinglePageView
from .views.index import DefaultPageView

# Define your urls here
urlpatterns = [
    # TODO: use custom converter https://docs.djangoproject.com/en/4.1/topics/http/urls/#registering-custom-path-converters
    path("<path:slug>", SinglePageView.as_view(), name="single-page"),
    path("", DefaultPageView.as_view()),
]
