from django.urls import path
from django.urls.converters import SlugConverter
from model_path_converter import register_model_converter

from apps.accounts.views.index import IndexView
from apps.accounts.views.members import SectionMembersView
from apps.accounts.views.membership import MyMembershipsView, NewSectionMembershipFormView
from apps.accounts.views.profile import MyProfileView, ProfileFinishFormView
from apps.accounts.views.user_detail import UserDetailView
from apps.sections.models import Section

register_model_converter(Section, field="space_slug", base=SlugConverter)

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("profile/finish", ProfileFinishFormView.as_view(), name="profile-finish"),
    path("profile", MyProfileView.as_view(), name="profile"),
    path(
        "membership/new/<section:section>",
        NewSectionMembershipFormView.as_view(),
        name="membership-new",
    ),
    path(
        "membership/new", NewSectionMembershipFormView.as_view(), name="membership-new"
    ),
    path("membership", MyMembershipsView.as_view(), name="membership"),
    path("section-members", SectionMembersView.as_view(), name="section-members"),

    path("user/<uuid:pk>", UserDetailView.as_view(), name="user-detail"),
    # path("", TemplateView.as_view(template_name="accounts/index.html")),
]
