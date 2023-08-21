from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import get_list_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView
from django_tables2 import Column, tables

from apps.esncards.forms.export import NewExportForm
from apps.esncards.models.export import Export
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestatables.columns import LabeledChoicesColumn, NaturalDatetimeColumn
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.middleware.user_membership import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import with_breadcrumb


class NewExportView(
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    HtmxFormMixin,
    SuccessMessageMixin,
    CreateView,
):
    template_name = "esncards/new_export.html"
    form_class = NewExportForm
    model = Export
    success_url = reverse_lazy("esncards:applications")
    success_message = _("Export successfully created.")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "applications": get_list_or_404(
                self.request.in_space_of_section.esncard_applications.order_by("last_name", "first_name"),
                pk__in=self.kwargs.get("applications", "").split(","),
            ),
        }
        return kwargs

    def get_form(self, form_class=None):
        f: NewExportForm = super().get_form(form_class)
        # TODO: maybe limit by state?
        f.fields["applications"].queryset = self.request.in_space_of_section.esncard_applications.all()
        return f

    def form_valid(self, form: NewExportForm):
        form.instance.section = self.request.in_space_of_section
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["applications"] = get_list_or_404(
            self.request.in_space_of_section.esncard_applications.order_by("last_name", "first_name"),
            pk__in=self.kwargs.get("applications", "").split(","),
        )
        return context


class ExportsTable(tables.Table):
    applications__count = Column(verbose_name=_("Applications count"))

    created = NaturalDatetimeColumn()

    state = LabeledChoicesColumn(
        Export.State,
        {},
    )

    class Meta:
        model = Export

        fields = ("created", "created_by")

        sequence = (
            "applications__count",
            "state",
            "created_by",
            "created",
            "...",
        )

        empty_text = _("No Exports")
        # row_attrs = {"data-id": lambda record: record.pk}


@with_breadcrumb(_("ESNcard"))
@with_breadcrumb(_("Exports"))
class ExportsView(EnsurePrivilegedUserViewMixin, FiestaTableView):
    request: HttpRequest
    template_name = "esncards/exports.html"
    table_class = ExportsTable
    # filterset_class = ESNcardApplicationsFilter
    model = Export

    def get_queryset(self):
        return self.request.in_space_of_section.esncard_exports.select_related("created_by")
