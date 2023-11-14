from __future__ import annotations

from django.db.models import Count

from apps.fiestatables.views.tables import FiestaMultiTableView
from apps.sections.models import SectionMembership, SectionUniversity
from apps.sections.tables.faculties import UniversityFacultiesTable
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.models.query import Q


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
