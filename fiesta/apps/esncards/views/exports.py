from __future__ import annotations

from django.shortcuts import get_list_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.esncards.forms.export import NewExportForm
from apps.esncards.models.export import Export
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class NewExportView(EnsurePrivilegedUserViewMixin, EnsureInSectionSpaceViewMixin, CreateView):
    template_name = "esncards/new_export.html"
    form_class = NewExportForm
    model = Export
    success_url = reverse_lazy("esncards:applications")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial"] = {
            "applications": get_list_or_404(
                self.request.in_space_of_section.esncard_applications.order_by("last_name", "first_name"),
                pk__in=self.kwargs.get("applications", "").split(","),
            )
        }
        return kwargs

    def get_form(self, form_class=None):
        f: NewExportForm = super().get_form(form_class)
        # TODO: maybe limit by state?
        f.fields["applications"].queryset = self.request.in_space_of_section.esncard_applications.all()

        return f

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["applications"] = get_list_or_404(
            self.request.in_space_of_section.esncard_applications.order_by("last_name", "first_name"),
            pk__in=self.kwargs.get("applications", "").split(","),
        )
        return context
