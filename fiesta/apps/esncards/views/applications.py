from __future__ import annotations

import django_tables2 as tables
from django.contrib.postgres.search import SearchVector
from django.forms import TextInput
from django.utils.translation import gettext_lazy as _
from django_filters import CharFilter, ChoiceFilter
from django_tables2 import Column

from apps.esncards.models import ESNcardApplication
from apps.fiestatables.columns import AvatarColumn, LabeledChoicesColumn, NaturalDatetimeColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_plugin_home_breadcrumb


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
    holder_photo = AvatarColumn(verbose_name=_("Photo"))
    birth_date = tables.DateColumn(verbose_name=_("Birth date"))
    nationality = Column(verbose_name=_("Nationality"))
    created = NaturalDatetimeColumn()

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


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Applications"))
class ApplicationsView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    request: HttpRequest
    template_name = "fiestatables/page.html"
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
