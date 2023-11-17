from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.db import models
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import CreateView

from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.fiestarequests.models import BaseRequestSystemConfiguration
from apps.fiestarequests.models.request import BaseRequestMatchProtocol, BaseRequestProtocol
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.views import AjaxViewMixin


class BaseTakeRequestView(
    PluginConfigurationViewMixin[BaseRequestSystemConfiguration],
    EnsureInSectionSpaceViewMixin,
    EnsureLocalUserViewMixin,
    AjaxViewMixin,
    HtmxFormViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_message = _("Request successfully matched!")
    match_model: type[BaseRequestMatchProtocol] | type[models.Model]
    form_url: str

    fiesta_request: BaseRequestProtocol

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if self.configuration and self.configuration.enable_note_from_matcher:
            form.fields["note"].required = True
        else:
            form.fields["note"].disabled = True
            form.fields["note"].widget = form.fields["note"].hidden_widget()

        return form

    def dispatch(self, request, *args, **kwargs):
        self.fiesta_request = get_object_or_404(
            self.get_queryset(),
            pk=kwargs.get("pk"),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["form_url"] = reverse(self.form_url, kwargs={"pk": self.fiesta_request.pk})
        return data

    def form_valid(self, form):
        match: BaseRequestMatchProtocol = form.instance
        match.request = self.fiesta_request
        match.matcher = self.request.user
        match.matcher_faculty = self.request.user.profile.faculty

        response = super().form_valid(form)

        self.fiesta_request.match = match
        self.fiesta_request.state = BaseRequestProtocol.State.MATCHED
        self.fiesta_request.save(update_fields=["state"])

        return response
