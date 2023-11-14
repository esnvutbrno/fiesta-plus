from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Count
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView

from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.views.tables import FiestaMultiTableView
from apps.sections.models import SectionMembership, SectionUniversity
from apps.sections.tables.faculties import UniversityFacultiesTable
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.universities.forms import UniversityForm
from apps.utils.models.query import Q
from apps.utils.views import AjaxViewMixin


class NewSectionUniversityView(
    EnsureInSectionSpaceViewMixin,
    EnsurePrivilegedUserViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    form_class = UniversityForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "sections/university_form.html"

    success_url = reverse_lazy("sections:section-universities")
    success_message = _("University created successfully")

    extra_context = {
        "form_url": reverse_lazy("sections:new-section-university"),
        # "base_page_template": "fiesta/base-variants/center-card-lg.html",
    }

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        SectionUniversity.objects.get_or_create(
            section=self.request.in_space_of_section,
            university=form.instance,
        )

        return response


class SectionUniversitiesView(
    EnsureInSectionSpaceViewMixin,
    EnsurePrivilegedUserViewMixin,
    FiestaMultiTableView,
):
    template_name = "sections/universities.html"
    model = SectionUniversity
    paginate_by = 30

    def get_queryset(self, *args, **kwargs):
        return self.request.in_space_of_section.universities.all()

    def get_tables(self):
        return [
            UniversityFacultiesTable(
                request=self.request,
                data=university.faculties.annotate(
                    members_count=Count(
                        "faculty_user_profiles",
                        distinct=True,
                        filter=Q(
                            faculty_user_profiles__user__memberships__section=self.request.in_space_of_section,
                            faculty_user_profiles__user__memberships__state=SectionMembership.State.ACTIVE,
                            faculty_user_profiles__user__memberships__role__in=(
                                SectionMembership.Role.MEMBER,
                                SectionMembership.Role.ADMIN,
                                SectionMembership.Role.EDITOR,
                            ),
                        ),
                    ),
                    internationals_count=Count(
                        "faculty_user_profiles",
                        distinct=True,
                        filter=Q(
                            faculty_user_profiles__user__memberships__section=self.request.in_space_of_section,
                            faculty_user_profiles__user__memberships__state=SectionMembership.State.ACTIVE,
                            faculty_user_profiles__user__memberships__role=SectionMembership.Role.INTERNATIONAL,
                        ),
                    ),
                ),
            )
            for university in self.object_list
        ]
