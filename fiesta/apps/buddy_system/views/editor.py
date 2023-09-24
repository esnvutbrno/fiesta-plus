from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, UpdateView
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_tables2 import Column, TemplateColumn, tables
from django_tables2.utils import Accessor

from apps.buddy_system.forms import BuddyRequestEditorForm, QuickBuddyMatchForm
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
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
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    state = ChoiceFilter(choices=BuddyRequest.State.choices)
    matched_when = ProperDateFromToRangeFilter(field_name="matched_at")

    matched_by_faculty = ModelChoiceFilter(
        queryset=related_faculties,
        label=_("Faculty of matcher"),
        field_name="matched_by__profile__home_faculty",
    )

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "issuer__last_name",
                "issuer__first_name",
                "matched_by__last_name",
                "matched_by__first_name",
                "state",
            )
        ).filter(search=value)

    class Meta(BaseFilterSet.Meta):
        pass


class BuddyRequestsTable(tables.Table):
    issuer__full_name_official = Column(
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username"),
        attrs={"a": {"x-data": lambda: "modal($el.href)", "x-bind": "bind"}},
        linkify=("buddy_system:editor-detail", {"pk": Accessor("pk")}),
        verbose_name=_("Request from"),
    )

    issuer__profile__picture = ImageColumn(verbose_name="🧑")

    matched_by_name = Column(
        accessor="matched_by.full_name_official",
        order_by=(
            "matched_by__last_name",
            "matched_by__first_name",
            "matched_by__username",
        ),
    )
    matched_by_email = Column(
        accessor="matched_by.email",
        visible=False,
    )

    matched_by_picture = ImageColumn(
        accessor="matched_by.profile.picture",
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
            "matched_by_name",
            "matched_by_picture",
            "matched_at",
            "match_request",
            "...",
        )
        empty_text = _("No buddy requests found")

        attrs = dict(tbody={"hx-disable": True})


@with_breadcrumb(_("Buddy System"))
@with_breadcrumb(_("Requests"))
class BuddyRequestsEditorView(
    EnsurePrivilegedUserViewMixin,
    FiestaTableView,
):
    request: HttpRequest
    table_class = BuddyRequestsTable
    filterset_class = RequestFilter

    def get_queryset(self):
        return self.request.in_space_of_section.buddy_system_requests.select_related(
            "issuer__profile",
        )


@with_breadcrumb(_("Buddy System"))
@with_object_breadcrumb()
class BuddyRequestEditorDetailView(
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
    CreateView,
):
    template_name = "buddy_system/editor/quick_match.html"
    ajax_template_name = "buddy_system/editor/quick_match_form.html"
    model = BuddyRequestMatch
    form_class = QuickBuddyMatchForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been matched.")

    def form_valid(self, form):
        request = get_object_or_404(BuddyRequest, pk=self.kwargs["pk"])
        form.instance.request = request
        request.state = BuddyRequest.State.MATCHED
        request.save(update_fields=["state"])

        return super().form_valid(form)
