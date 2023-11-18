from __future__ import annotations

from django.urls import path
from django.views.generic import RedirectView

from apps.accounts.views.index import AfterLoginRedirectView
from apps.accounts.views.membership import MyMembershipsView, NewSectionMembershipFormView
from apps.accounts.views.profile import MyProfileDetailView, MyProfileUpdateView, ProfileFinishFormView

app_name = "accounts"
urlpatterns = [
    path("", RedirectView.as_view(pattern_name="accounts:my-profile"), name="index"),
    path("my-profile", MyProfileDetailView.as_view(), name="my-profile"),
    path("my-profile/update", MyProfileUpdateView.as_view(), name="my-profile-update"),
    path("profile/finish", ProfileFinishFormView.as_view(), name="profile-finish"),
    path(
        "membership/new/<section:section>",
        NewSectionMembershipFormView.as_view(),
        name="membership-new",
    ),
    path("membership/new", NewSectionMembershipFormView.as_view(), name="membership-new"),
    path("membership", MyMembershipsView.as_view(), name="membership"),
    # path("", TemplateView.as_view(template_name="accounts/index.html")),
    # path("login", LoginViewNotInSectionSpace.as_view(), name="login"),
    path("after-login", AfterLoginRedirectView.as_view(), name="after-login"),
]
