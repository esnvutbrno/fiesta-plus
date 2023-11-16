from __future__ import annotations

from django.urls import path

from ..accounts.models.profile import user_profile_picture_storage
from .views import PickupSystemIndexView
from .views.editor import PickupRequestEditorDetailView, PickupRequestsEditorView, QuickPickupMatchView
from .views.matches import MyPickups
from .views.matching import IssuerPictureServeView, MatcherPictureServeView, MatchingRequestsView, TakePickupRequestView
from .views.request import NewPickupRequestView

urlpatterns = [
    path("", PickupSystemIndexView.as_view(), name="index"),
    path("new-request", NewPickupRequestView.as_view(), name="new-request"),
    path("requests", PickupRequestsEditorView.as_view(), name="requests"),
    path("my-pickups", MyPickups.as_view(), name="my-pickups"),
    path("matching-requests", MatchingRequestsView.as_view(), name="matching-requests"),
    path(
        "take-request/<uuid:pk>",
        TakePickupRequestView.as_view(),
        name="take-pickup-request",
    ),
    path("detail/<uuid:pk>", PickupRequestEditorDetailView.as_view(), name="editor-detail"),
    path("quick-match/<uuid:pk>", QuickPickupMatchView.as_view(), name="quick-match"),
    # serve profile picture with proxy view
    IssuerPictureServeView.as_url(user_profile_picture_storage, url_name="serve-issuer-profile-picture"),
    MatcherPictureServeView.as_url(user_profile_picture_storage, url_name="serve-matcher-profile-picture"),
]
