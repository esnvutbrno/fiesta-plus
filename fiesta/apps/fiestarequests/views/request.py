from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView

from apps.accounts.models import UserProfile
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.sections.views.mixins.membership import EnsureInternationalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.views import AjaxViewMixin


class BaseNewRequestView(
    EnsureInSectionSpaceViewMixin,
    EnsureInternationalUserViewMixin,
    SuccessMessageMixin,
    AjaxViewMixin,
    HtmxFormMixin,
    CreateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    def get_initial(self):
        p: UserProfile = self.request.user.profile_or_none
        return {
            "responsible_section": self.request.in_space_of_section,
            "issuer": self.request.user,
            "issuer_faculty": p.faculty if p else None,
            # "interests": p.interests if p else None,
        }

    def form_valid(self, form):
        # override to be sure
        form.instance.responsible_section = self.request.in_space_of_section
        form.instance.issuer = self.request.user

        return super().form_valid(form)
