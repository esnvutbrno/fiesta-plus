from __future__ import annotations
from django.urls import path

from .views import OpenHoursIndexView
from .views.index import MapView

# Define your urls here
urlpatterns = [
    path("", OpenHoursIndexView.as_view()),
    path("map", MapView.as_view(), name="map"),
]
