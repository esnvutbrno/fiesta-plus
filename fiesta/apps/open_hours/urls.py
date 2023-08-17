from django.urls import path, include

from .views import OpenHoursIndexView

# Define your urls here
urlpatterns = [
    path('', OpenHoursIndexView.as_view())
]
