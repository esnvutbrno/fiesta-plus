# Define your urls here
from __future__ import annotations

from django.urls import path
from django.urls.converters import SlugConverter
from model_path_converter import register_model_converter

from apps.accounts.views.membership import MembershipDetailView
from apps.sections.models import Section
from apps.sections.views.choose_space import ChooseSpaceView
from apps.sections.views.members import SectionMembersView

register_model_converter(Section, field="space_slug", base=SlugConverter)
urlpatterns = [
    path("section-members", SectionMembersView.as_view(), name="section-members"),
    path("user/<uuid:pk>", MembershipDetailView.as_view(), name="membership-detail"),
    path("choose-section", ChooseSpaceView.as_view(), name="choose-space"),
]
