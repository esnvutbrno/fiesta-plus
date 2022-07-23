from django.urls import path

from apps.accounts.views.index import IndexView
from apps.accounts.views.members import SectionMembersView
from apps.accounts.views.membership import MembershipView, NewSectionMembershipFormView
from apps.accounts.views.profile import MyProfileView, ProfileFinishFormView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("profile/finish", ProfileFinishFormView.as_view(), name="profile-finish"),
    path("profile", MyProfileView.as_view(), name="profile"),
    path("membership/new", NewSectionMembershipFormView.as_view(), name="membership-new"),
    path("membership", MembershipView.as_view(), name="membership"),
    path("section-members", SectionMembersView.as_view(), name="section-members"),
    # path("", TemplateView.as_view(template_name="accounts/index.html")),
]
