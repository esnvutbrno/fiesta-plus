from django.urls import path

from .views import BuddySystemIndexView
# Define your urls here
from .views.request import WannaBuddyView

urlpatterns = [
    path('', BuddySystemIndexView.as_view()),
    path('wanna-buddy', WannaBuddyView.as_view(), name='wanna-buddy'),
]
