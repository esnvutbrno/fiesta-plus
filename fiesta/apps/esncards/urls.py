from django.urls import include, path

from .views import EsncardsIndexView
from .views.application import ESNcardApplicationCreateView

urlpatterns = [
    path("create", ESNcardApplicationCreateView.as_view()),
    path("", EsncardsIndexView.as_view()),
]
