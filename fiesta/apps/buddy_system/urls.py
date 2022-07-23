from django.urls import path

from .views import BuddySystemIndexView

# Define your urls here
urlpatterns = [
    path('', BuddySystemIndexView.as_view())
]
