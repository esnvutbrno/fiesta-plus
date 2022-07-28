from django.urls import path

from .views import BuddySystemIndexView
from .views.editor import RequestsEditorView
from .views.matching import MatchingRequestsView, ProfilePictureServeView
from .views.request import WannaBuddyView, SignUpBeforeRequestView, NewRequestView
from ..accounts.models.profile import user_profile_picture_storage

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
    path("matching-requests", MatchingRequestsView.as_view(), name="matching-requests"),
    ProfilePictureServeView.as_url(
        user_profile_picture_storage, url_name="serve-issuer-profile-picture"
    ),
]
