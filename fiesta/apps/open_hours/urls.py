from __future__ import annotations
from django.urls import path

from .views import OpenHoursIndexView
from .views.editor import CreateOpenHours, UpdateOpenHours
from .views.index import MapView

# Define your urls here
urlpatterns = [
    path("", OpenHoursIndexView.as_view(), name="index"),
    path("map", MapView.as_view(), name="map"),
    path("new-oh", CreateOpenHours.as_view(), name="new-oh"),
    path("update-oh/<uuid:pk>", UpdateOpenHours.as_view(), name="update-oh"),
]
