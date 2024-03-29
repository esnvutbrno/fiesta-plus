from __future__ import annotations

from django.urls import path
from django.urls.converters import SlugConverter
from django.views.generic import RedirectView
from model_path_converter import register_model_converter

from apps.sections.models import Section
from apps.sections.views.choose_space import ChooseSpaceView
from apps.sections.views.internationals import SectionInternationalsView
from apps.sections.views.members import ChangeMembershipStateFormView, SectionMembersView
from apps.sections.views.membership import MembershipDetailView, UserDetailRedirectView
from apps.sections.views.membership_editor import MembershipRoleEditorView, MembershipStateEditorView
from apps.sections.views.plugins import (
    ChangePluginConfigurationFormView,
    ChangePluginStateFormView,
    SectionPluginsView,
    SetupPluginFormView,
)
from apps.sections.views.stats import SectionStatsView
from apps.sections.views.universities import (
    NewSectionFacultyView,
    NewSectionUniversityView,
    SectionUniversitiesView,
    UpdateSectionFacultyView,
    UpdateSectionUniversityView,
)

register_model_converter(Section, field="space_slug", base=SlugConverter)
urlpatterns = [
    # TODO: homepage for esn section plugin?
    path("", RedirectView.as_view(pattern_name="sections:section-members"), name="index"),
    path("universities", SectionUniversitiesView.as_view(), name="section-universities"),
    path("universities/new", NewSectionUniversityView.as_view(), name="new-section-university"),
    path("universities/<uuid:pk>", UpdateSectionUniversityView.as_view(), name="update-section-university"),
    path("universities/<uuid:pk>/faculties/new", NewSectionFacultyView.as_view(), name="new-section-faculty"),
    path("universities/faculties/<uuid:pk>", UpdateSectionFacultyView.as_view(), name="update-section-faculty"),
    path("section-members", SectionMembersView.as_view(), name="section-members"),
    path("section-internationals", SectionInternationalsView.as_view(), name="section-internationals"),
    path("section-stats", SectionStatsView.as_view(), name="section-stats"),
    path("section-plugins", SectionPluginsView.as_view(), name="section-plugins"),
    path(
        "membership-state-editor/<uuid:pk>",
        MembershipStateEditorView.as_view(),
        name="membership-state-editor",
    ),
    path(
        "membership-role-editor/<uuid:pk>",
        MembershipRoleEditorView.as_view(),
        name="membership-role-editor",
    ),
    path("membership-form/<uuid:pk>", ChangeMembershipStateFormView.as_view(), name="change-membership-state-form"),
    path("membership/<uuid:pk>", MembershipDetailView.as_view(), name="membership-detail"),
    path("user/<int:pk>", UserDetailRedirectView.as_view(), name="user-detail"),
    path("choose-section", ChooseSpaceView.as_view(), name="choose-space"),
    path("plugin-setup", SetupPluginFormView.as_view(), name="setup-plugin"),
    path("plugin-state/<uuid:pk>", ChangePluginStateFormView.as_view(), name="change-plugin-state"),
    path(
        "plugin-configuration/<uuid:pk>",
        ChangePluginConfigurationFormView.as_view(),
        name="change-plugin-configuration",
    ),
]
