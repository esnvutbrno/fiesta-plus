from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ObjectDoesNotExist
from django.db import models, transaction
from django.urls import reverse
from django.views.generic import UpdateView

from apps.accounts.models import User, UserProfile
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.fiestarequests.models.request import BaseRequestProtocol
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.views import AjaxViewMixin


class BaseQuickRequestMatchView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    # to be set by subclasses
    form_url: str
    match_model: type[models.Model]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse(self.form_url, kwargs={"pk": self.object.pk})
        return context

    def get_initial(self):
        try:
            matcher: User = self.get_object().match.matcher
            profile: UserProfile = matcher.profile_or_none
            return {
                "matcher": matcher,
                # SectionPluginsValidator ensures that faculty is required if PickupSystem is enabled
                "matcher_faculty": profile.faculty if profile else None,
            }
        except ObjectDoesNotExist:
            return {}

    @transaction.atomic
    def form_valid(self, form):
        br: BaseRequestProtocol | models.Model = form.instance

        try:
            if br.match:
                # could be already matched by someone else
                br.match.delete()
        except ObjectDoesNotExist:
            pass

        matcher: User = form.cleaned_data.get("matcher")

        match = self.match_model(
            request=br,
            matcher=matcher,
            matcher_faculty=matcher.profile_or_none.faculty,
        )

        match.save()

        br.state = BaseRequestProtocol.State.MATCHED
        br.save(update_fields=["state"])

        return super().form_valid(form)
