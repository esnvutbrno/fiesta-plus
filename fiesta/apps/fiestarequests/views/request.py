from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.forms import HiddenInput
from django.views.generic import CreateView

from apps.accounts.models import UserProfile
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.fiestarequests.forms.request import USER_PROFILE_CONTACT_FIELDS, BaseNewRequestForm
from apps.sections.views.mixins.membership import EnsureInternationalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.views import AjaxViewMixin


class BaseNewRequestView(
    EnsureInSectionSpaceViewMixin,
    EnsureInternationalUserViewMixin,
    SuccessMessageMixin,
    AjaxViewMixin,
    HtmxFormViewMixin,
    CreateView,
):
    form_class = BaseNewRequestForm
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        p: UserProfile = self.request.user.profile_or_none
        # hide all filled fields
        for k in USER_PROFILE_CONTACT_FIELDS:
            if getattr(p, k, None):
                form.fields[k].widget = HiddenInput(form.fields[k].widget.attrs)

        return form

    def get_initial(self):
        p: UserProfile = self.request.user.profile_or_none
        return dict(
            issuer_faculty=p.faculty if p else None,
        ) | {
            # default values for all contact fields
            k: getattr(p, k)
            for k in USER_PROFILE_CONTACT_FIELDS
        }

    @transaction.atomic
    def form_valid(self, form):
        # override to be sure
        form.instance.responsible_section = self.request.in_space_of_section
        form.instance.issuer = self.request.user

        profile: UserProfile = self.request.user.profile_or_none
        if profile and not profile.faculty:
            profile.faculty = form.cleaned_data["issuer_faculty"]

        # save all contact fields
        for k in USER_PROFILE_CONTACT_FIELDS:
            if v := form.cleaned_data.get(k):
                setattr(profile, k, v)

        profile.save(update_fields=["faculty"] + list(USER_PROFILE_CONTACT_FIELDS.keys()))

        return super().form_valid(form)
