from django.urls import path, include

from .views import EventsIndexView

# Define your urls here
urlpatterns = [
    path('', EventsIndexView.as_view())
]
