# Define your urls here
from __future__ import annotations

from django.urls import path
from django.urls.converters import SlugConverter
from model_path_converter import register_model_converter

from apps.sections.models import Section
from apps.sections.views.choose_space import ChooseSpaceView
from apps.sections.views.members import ChangeMembershipStateView, MembershipDetailView, SectionMembersView
from apps.sections.views.settings import (
    ChangePluginConfigurationFormView,
    ChangePluginStateFormView,
    SectionSettingsView,
)
from apps.sections.views.stats import SectionStatsView

register_model_converter(Section, field="space_slug", base=SlugConverter)
urlpatterns = [
    path("section-members", SectionMembersView.as_view(), name="section-members"),
    path("section-stats", SectionStatsView.as_view(), name="section-stats"),
    path("section-settings", SectionSettingsView.as_view(), name="section-settings"),
    path("membership-state/<uuid:pk>", ChangeMembershipStateView.as_view(), name="change-membership-state"),
    path("membership/<uuid:pk>", MembershipDetailView.as_view(), name="membership-detail"),
    path("choose-section", ChooseSpaceView.as_view(), name="choose-space"),
    path("plugin-state/<uuid:pk>", ChangePluginStateFormView.as_view(), name="change-plugin-state"),
    path(
        "plugin-configuration/<uuid:pk>",
        ChangePluginConfigurationFormView.as_view(),
        name="change-plugin-configuration",
    ),
]
