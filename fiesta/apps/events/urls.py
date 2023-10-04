from __future__ import annotations

from django.urls import path

from .views import EventsIndexView
from .views.event import AddEventView, EventDetailView, ParticipantsView, UpdateEventView

# Define your urls here

app_name = "events"

urlpatterns = [
    path('', EventsIndexView.as_view(), name="index"),
    path('add-event', AddEventView.as_view(), name="add-event"),
    path('event-update/<uuid:pk>', UpdateEventView.as_view(), name="event-update"),
    path('event-detail/<uuid:pk>', EventDetailView.as_view(), name="event-detail"),
    path("event-detail/<uuid:pk>/participants", ParticipantsView.as_view(), name="participants"), # event-detail/<uuid:pk>/

]
