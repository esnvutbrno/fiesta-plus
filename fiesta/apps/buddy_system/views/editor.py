from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.db import transaction
from django.forms import TextInput
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_filters import CharFilter, ChoiceFilter, ModelChoiceFilter
from django_tables2 import Column, TemplateColumn, tables
from django_tables2.utils import Accessor

from apps.accounts.models import User, UserProfile
from apps.buddy_system.forms import BuddyRequestEditorForm, QuickBuddyMatchForm
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.columns import AvatarColumn, NaturalDatetimeColumn
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
    matched_when = ProperDateFromToRangeFilter(
        field_name="match__created",
    )

    matcher_faculty = ModelChoiceFilter(
        queryset=related_faculties,
        label=_("Faculty of matcher"),
        field_name="match__matcher__profile__faculty",
    )

    def filter_search(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "issuer__last_name",
                "issuer__first_name",
                "match__matcher__last_name",
                "match__matcher__first_name",
                "state",
            )
        ).filter(search=value)

    class Meta(BaseFilterSet.Meta):
        pass


class BuddyRequestsTable(tables.Table):
    issuer_name = Column(
        accessor="issuer.full_name_official",
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username"),
        attrs={"a": {"x-data": lambda: "modal($el.href)", "x-bind": "bind"}},
        linkify=("buddy_system:editor-detail", {"pk": Accessor("pk")}),
        verbose_name=_("Issuer"),
    )

    issuer_picture = AvatarColumn(accessor="issuer.profile.picture", verbose_name="🧑")

    matcher_name = Column(
        accessor="match.matcher.full_name_official",
        order_by=(
            "match__matcher__last_name",
            "match__matcher__first_name",
            "match__matcher__username",
        ),
        linkify=("sections:user-detail", {"pk": Accessor("match.matcher.pk")}),
    )
    matcher_email = Column(
        accessor="match.matcher.email",
        visible=False,
    )

    matcher_picture = AvatarColumn(
        accessor="match.matcher.profile.picture",
        verbose_name=_("Matcher"),
    )

    match_request = TemplateColumn(
        template_name="buddy_system/parts/requests_editor_match_btn.html",
        exclude_from_export=True,
        order_by="match",
    )

    requested = NaturalDatetimeColumn(verbose_name=_("Requested"), accessor="created")
    matched = NaturalDatetimeColumn(
        accessor="match.created",
        verbose_name=_("Matched"),
        attrs={"td": {"title": None}},  # TODO: fix attrs accessor
    )

    class Meta:
        model = BuddyRequest
        # TODO: dynamic by section preferences
        fields = ("state",)
        sequence = (
            "issuer_name",
            "issuer_picture",
            "state",
            "matcher_name",
            "matcher_picture",
            "requested",
            "matched",
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
    UpdateView,
):
    template_name = "buddy_system/editor/quick_match.html"
    ajax_template_name = "buddy_system/editor/quick_match_form.html"
    model = BuddyRequest
    form_class = QuickBuddyMatchForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been matched.")

    def get_initial(self):
        try:
            matcher: User = self.get_object().match.matcher
            profile: UserProfile = matcher.profile_or_none
            return {
                "matcher": matcher,
                # SectionPluginsValidator ensures that faculty is required if BuddySystem is enabled
                "matcher_faculty": profile.faculty if profile else None,
            }
        except BuddyRequestMatch.DoesNotExist:
            return {}

    @transaction.atomic
    def form_valid(self, form):
        br: BuddyRequest = form.instance

        try:
            if br.match:
                # could be already matched by someone else
                br.match.delete()
        except BuddyRequestMatch.DoesNotExist:
            pass

        matcher: User = form.cleaned_data.get("matcher")

        match = BuddyRequestMatch(
            request=br,
            matcher=matcher,
            matcher_faculty=matcher.profile_or_none.faculty,
        )

        match.save()

        br.state = BuddyRequest.State.MATCHED
        br.save(update_fields=["state"])

        return super().form_valid(form)
