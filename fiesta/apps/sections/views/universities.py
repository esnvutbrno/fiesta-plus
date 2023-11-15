from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView

from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.views.tables import FiestaMultiTableView
from apps.sections.models import SectionMembership, SectionUniversity
from apps.sections.tables.faculties import UniversityFacultiesTable
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.universities.forms import FacultyForm, UniversityForm
from apps.universities.models import Faculty, University
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
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

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


class UpdateSectionUniversityView(
    EnsureInSectionSpaceViewMixin,
    EnsurePrivilegedUserViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = UniversityForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_url = reverse_lazy("sections:section-universities")
    success_message = _("University changed successfully")

    def get_queryset(self):
        return University.objects.filter(university_sections__section=self.request.in_space_of_section)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse("sections:update-section-university", kwargs={"pk": self.object.pk})
        return context


class NewSectionFacultyView(
    EnsureInSectionSpaceViewMixin,
    EnsurePrivilegedUserViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    form_class = FacultyForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_url = reverse_lazy("sections:section-universities")
    success_message = _("Faculty created successfully")

    university: University = None

    def dispatch(self, request, *args, **kwargs):
        self.university = get_object_or_404(University, pk=kwargs.get("pk"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse("sections:new-section-faculty", kwargs={"pk": self.university.pk})
        return context

    def form_valid(self, form):
        form.instance.university = self.university
        return super().form_valid(form)


class UpdateSectionFacultyView(
    EnsureInSectionSpaceViewMixin,
    EnsurePrivilegedUserViewMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = FacultyForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_url = reverse_lazy("sections:section-universities")
    success_message = _("Faculty changed successfully")

    def get_queryset(self):
        return Faculty.objects.filter(university__university_sections__section=self.request.in_space_of_section)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse("sections:update-section-faculty", kwargs={"pk": self.object.pk})
        return context


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
                    users_count=Count(
                        "faculty_user_profiles",
                        distinct=True,
                    ),
                ),
            )
            for university in self.object_list
        ]
