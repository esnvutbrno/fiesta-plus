from __future__ import annotations

from django.urls import path

from .views import EventsIndexView
from .views.event import AddEventView, EventDetailView, ParticipantsView, UpdateEventView, ConfirmEvent, EventParticipantRegister
from .views.organizer import OrganizersView, AddOrganizerView, UpdateOrganizerRole, DeleteOrganizerView
from .views.price import PriceView, PriceUpdate, PriceDelete
from .views.place import PlaceView, AddPlaceView, UpdatePlaceView, DeletePlaceView

# Define your urls here

app_name = "events"

urlpatterns = [
    path('', EventsIndexView.as_view(), name="index"),
    path('add-event', AddEventView.as_view(), name="add-event"),
    path('event-update/<uuid:pk>', UpdateEventView.as_view(), name="event-update"),
    path('event-detail/<uuid:pk>', EventDetailView.as_view(), name="event-detail"),
    path("event-detail/<uuid:pk>/participants", ParticipantsView.as_view(), name="participants"), # event-detail/<uuid:pk>/
    path("event-detail/<uuid:pk>/organizers", OrganizersView.as_view(), name="organizers"), 
    path("event-detail/<uuid:pk>/organizers/<uuid:pko>", UpdateOrganizerRole.as_view(), name="role-change"), # event-detail/<uuid:pk>/
    path("event-detail/<uuid:pk>/organizers/delete/<uuid:pko>", DeleteOrganizerView.as_view(), name="organizer-delete"), # event-detail/<uuid:pk>/
    path("event-detail/<uuid:pk>/organizers/add", AddOrganizerView.as_view(), name="organizer-add"),
    path("event-update/<uuid:pk>/price", PriceView.as_view(), name="price"),
    path("event-update/<uuid:pk>/price/<uuid:pricepk>", PriceUpdate.as_view(), name="price-update"),
    path("event-update/<uuid:pk>/price-delete/<uuid:pricepk>", PriceDelete.as_view(), name="price-delete"),
    path("place", PlaceView.as_view(), name="place"),
    path("place/add", AddPlaceView.as_view(), name="place-add"),
    path("event-update/<uuid:pk>/place/add", AddPlaceView.as_view(), name="eventplace-add"),
    path("place/update/<uuid:pk>", UpdatePlaceView.as_view(), name="place-update"),
    path("place/delete/<uuid:pk>", DeletePlaceView.as_view(), name="place-delete"),
    path("event-detail/<uuid:pk>/confirm", ConfirmEvent.as_view(), name="event-confirm"),
    path("event-detail/<uuid:pk>/register", EventParticipantRegister.as_view(), name="event-register"),
]
