from django.urls import path

from ..accounts.models.profile import user_profile_picture_storage
from .views import BuddySystemIndexView
from .views.editor import RequestEditorDetailView, RequestsEditorView
from .views.matching import MatchingRequestsView, ProfilePictureServeView, TakeBuddyRequestView
from .views.request import NewRequestView, SignUpBeforeRequestView, WannaBuddyView

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
    path(
        "take-request/<uuid:pk>",
        TakeBuddyRequestView.as_view(),
        name="take-buddy-request",
    ),
    path("detail/<uuid:pk>", RequestEditorDetailView.as_view(), name="editor-detail"),
    # serve profile picture with proxy view
    ProfilePictureServeView.as_url(user_profile_picture_storage, url_name="serve-issuer-profile-picture"),
]
