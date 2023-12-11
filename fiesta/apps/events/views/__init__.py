from .index import EventsIndexView
from .event import AddEventView, EventDetailView, UpdateEventView, ParticipantsView
from .price import AddPriceView, AddPriceView, DeletePriceView
from .place import PlaceView, AddPlaceView, UpdatePlaceView, DeletePlaceView

__all__ = [
    "EventsIndexView",
    "AddEventView",
    "EventDetailView",
    "UpdateEventView",
    "PlaceView",
    "AddPlaceView",
    "UpdatePlaceView",
    "DeletePlaceView",
    "AddPriceView",
    "DeletePriceView",
    "PriceDelete",
    "ParticipantsView",
]
