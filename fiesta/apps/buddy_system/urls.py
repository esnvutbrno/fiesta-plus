from django.urls import path

from .views import BuddySystemIndexView
from .views.editor import RequestsEditorView
from .views.request import WannaBuddyView, SignUpBeforeRequestView, NewRequestView

urlpatterns = [
    path("", BuddySystemIndexView.as_view(), name="index"),
    path("wanna-buddy", WannaBuddyView.as_view(), name="wanna-buddy"),
    path(
        "sign-up-before-request",
        SignUpBeforeRequestView.as_view(),
        name="sign-up-before-request",
    ),
    path("new-request", NewRequestView.as_view(), name="new-request"),
    path("requests", RequestsEditorView.as_view(), name="requests-editor"),
]
