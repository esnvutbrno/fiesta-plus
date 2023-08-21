from __future__ import annotations

import django_tables2 as tables
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_filters import CharFilter, ChoiceFilter
from django_tables2 import Column, TemplateColumn

from apps.esncards.forms.application import ApproveESNcardApplicationForm
from apps.esncards.models import ESNcardApplication
from apps.fiestatables.columns import ExpandableImageColumn, LabeledChoicesColumn, NaturalDatetimeColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import with_breadcrumb


class ESNcardApplicationsFilter(BaseFilterSet):
    search = CharFilter(
        method="filter_search",
        label=_("Search"),
        widget=TextInput(attrs={"placeholder": _("Hannah, Diego, Joe...")}),
    )
    state = ChoiceFilter(choices=ESNcardApplication.State.choices, label=_("State"))

    created = ProperDateFromToRangeFilter(label=_("Created"))

    class Meta(BaseFilterSet.Meta):
        pass

    def filter_search(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("user__last_name", "user__first_name", "state")).filter(
            search=value
        )


class ESNcardApplicationsTable(tables.Table):
    user__full_name_official = Column(
        verbose_name=_("Issuer"),
        order_by=("user__last_name", "user__first_name", "user__username"),
        linkify=(
            "esncards:application_detail",
            dict(
                pk=tables.A("pk"),
            ),
        ),
        attrs=dict(a={"hx-disable": True}),  # TODO: do it properly
    )
    holder_photo = ExpandableImageColumn(verbose_name=_("Photo"))
    birth_date = tables.DateColumn(verbose_name=_("Birth date"))
    nationality = Column(verbose_name=_("Nationality"))
    created = NaturalDatetimeColumn()

    actions = TemplateColumn(
        template_name="esncards/parts/application_action_column.html",
        extra_context={
            "ApplicationState": ESNcardApplication.State,
        },
        orderable=False,
        exclude_from_export=True,
        verbose_name="",
    )

    state = LabeledChoicesColumn(
        ESNcardApplication.State,
        {
            ESNcardApplication.State.CREATED: "🆕",
            ESNcardApplication.State.ACCEPTED: "🆗",
            ESNcardApplication.State.READY_TO_PICKUP: "📦",
            ESNcardApplication.State.ISSUED: "✅",
            ESNcardApplication.State.DECLINED: "⛔",
            ESNcardApplication.State.CANCELLED: "🗑️",
        },
    )

    class Meta:
        model = ESNcardApplication

        fields = ("state", "created")

        sequence = (
            "user__full_name_official",
            "nationality",
            "birth_date",
            "holder_photo",
            "created",
            "...",
        )

        empty_text = _("No ESNcard Applications")
        # row_attrs = {"data-id": lambda record: record.pk}


@with_breadcrumb(_("ESNcard"))
@with_breadcrumb(_("Applications"))
class ApplicationsView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    filterset: BaseFilterSet
    request: HttpRequest
    template_name = "esncards/applications.html"
    table_class = ESNcardApplicationsTable
    filterset_class = ESNcardApplicationsFilter
    model = ESNcardApplication

    def get_queryset(self):
        return self.request.in_space_of_section.esncard_applications.filter(
            state__in=(
                # TODO: limit somehow?
                ESNcardApplication.State.CREATED,
                ESNcardApplication.State.ACCEPTED,
                ESNcardApplication.State.READY_TO_PICKUP,
                ESNcardApplication.State.ISSUED,
                ESNcardApplication.State.DECLINED,
                ESNcardApplication.State.CANCELLED,
            )
        ).select_related("user")

    def get_table_kwargs(self):
        kwargs = super().get_table_kwargs()
        state_value: ChoiceFilter = self.filterset.is_bound and self.filterset.form.cleaned_data.get("state")

        dynamic_columns = {"select_for_export"}

        match state_value:
            case None | False:
                kwargs["exclude"] = dynamic_columns

            case ESNcardApplication.State.ACCEPTED.value:
                kwargs["exclude"] = dynamic_columns - {"select_for_export"}

        return kwargs


class ChangeApplicationStateView(
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    # HtmxFormMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = ApproveESNcardApplicationForm
    success_message = _("Application has been approved.")
    success_url = reverse_lazy("esncards:applications")
    template_name = "esncards/parts/application_action_column.html"

    def get_queryset(self):
        return self.request.in_space_of_section.esncard_applications
