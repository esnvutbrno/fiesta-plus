from django.urls import path, include

from .views import EventsIndexView
from .views.event import AddEventView, EventView
# Define your urls here

app_name="events"
urlpatterns = [
    path('', EventView.as_view(), name="index"),
    path('add-event', AddEventView.as_view(), name="add-event"),
]
