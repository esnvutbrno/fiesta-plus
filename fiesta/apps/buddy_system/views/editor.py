from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_filters import ChoiceFilter, ModelChoiceFilter
from django_tables2 import Column, TemplateColumn, tables
from django_tables2.utils import Accessor

from apps.buddy_system.forms import BuddyRequestEditorForm, QuickBuddyMatchForm
from apps.buddy_system.models import BuddyRequest
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.columns import ImageColumn, NaturalDatetimeColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.middleware.section_space import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.universities.models import Faculty
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb
from apps.utils.views import AjaxViewMixin


def related_faculties(request: HttpRequest):
    return Faculty.objects.filter(university__section=request.in_space_of_section)


class RequestFilter(BaseFilterSet):
    state = ChoiceFilter(choices=BuddyRequest.State.choices)
    matched_when = ProperDateFromToRangeFilter(field_name="matched_at")

    matched_by_faculty = ModelChoiceFilter(
        queryset=related_faculties,
        label=_("Faculty of matcher"),
        field_name="matched_by__profile__home_faculty",
    )

    class Meta(BaseFilterSet.Meta):
        pass


class RequestTable(tables.Table):
    issuer__full_name_official = Column(
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username"),
        attrs={"a": {"x-data": lambda: "modal($el.href)", "x-bind": "bind"}},
        linkify=("buddy_system:editor-detail", {"pk": Accessor("pk")}),
        verbose_name=_("Request from"),
    )

    issuer__profile__picture = ImageColumn(verbose_name=_("Issuer"))

    matched_by__full_name_official = Column(
        order_by=(
            "matched_by__last_name",
            "matched_by__first_name",
            "matched_by__username",
        ),
    )
    matched_by__email = Column(
        visible=False,
    )

    matched_by__profile__picture = ImageColumn(
        verbose_name=_("Buddy"),
    )

    match_request = TemplateColumn(
        template_name="buddy_system/parts/requests_editor_match_btn.html",
        exclude_from_export=True,
        order_by="matched_at",
    )

    matched_at = NaturalDatetimeColumn()

    class Meta:
        model = BuddyRequest
        # TODO: dynamic by section preferences
        fields = ("state",)
        sequence = (
            "issuer__full_name_official",
            "issuer__profile__picture",
            "state",
            "matched_by__full_name_official",
            "matched_by__profile__picture",
            "matched_at",
            "match_request",
            "...",
        )

        attrs = dict(tbody={"hx-disable": True})


@with_breadcrumb(_("Buddy System"))
@with_breadcrumb(_("Requests"))
class RequestsEditorView(
    EnsurePrivilegedUserViewMixin,
    FiestaTableView,
):
    request: HttpRequest
    table_class = RequestTable
    filterset_class = RequestFilter

    def get_queryset(self):
        return self.request.in_space_of_section.buddy_system_requests.select_related(
            "issuer__profile",
        )


@with_breadcrumb(_("Buddy System"))
@with_object_breadcrumb()
class RequestEditorDetailView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "buddy_system/editor/detail.html"
    ajax_template_name = "buddy_system/editor/detail_form.html"
    model = BuddyRequest
    form_class = BuddyRequestEditorForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been updated.")


@with_breadcrumb(_("Quick Buddy Match"))
@with_object_breadcrumb()
class QuickBuddyMatchView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "buddy_system/editor/quick_match.html"
    ajax_template_name = "buddy_system/editor/quick_match_form.html"
    model = BuddyRequest
    form_class = QuickBuddyMatchForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been matched.")
