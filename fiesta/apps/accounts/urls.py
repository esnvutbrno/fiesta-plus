from django.urls import path

from apps.accounts.views.membership import MembershipView, NewMembershipFormView
from apps.accounts.views.profile import MyProfileView, ProfileFinishFormView, ProfileUpdateFormView

urlpatterns = [
    path("profile/finish", ProfileFinishFormView.as_view(), name="profile-finish"),
    path("profile/update", ProfileUpdateFormView.as_view(), name="profile-update"),
    path("profile", MyProfileView.as_view(), name="profile"),
    path("changepswd", MyProfileView.as_view(), name="changepswd"),
    path("membership/new", NewMembershipFormView.as_view(), name="membership-new"),
    path("membership", MembershipView.as_view(), name="membership"),
    # path("", TemplateView.as_view(template_name="accounts/index.html")),
]
