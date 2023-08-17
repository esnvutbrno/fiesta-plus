from __future__ import annotations

from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from apps.open_hours.forms.open_hours import OpenHoursForm
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin


class CreateOpenHours(
    EnsurePrivilegedUserViewMixin,
    CreateView,
):
    form_class = OpenHoursForm
    template_name = "open_hours/open_hours_form.html"
    success_url = reverse_lazy("open_hours:index")

    def form_valid(self, form):
        form.instance.section = self.request.in_space_of_section
        return super().form_valid(form)


class UpdateOpenHours(
    EnsurePrivilegedUserViewMixin,
    UpdateView,
):
    form_class = OpenHoursForm
    template_name = "open_hours/open_hours_form.html"
    success_url = reverse_lazy("open_hours:index")

    def get_queryset(self):
        return self.request.in_space_of_section.open_hours.all()
