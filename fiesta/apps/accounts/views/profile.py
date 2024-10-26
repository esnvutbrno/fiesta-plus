from __future__ import annotations

from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView, UpdateView

from apps.accounts.forms.profile import UserProfileFinishForm
from apps.accounts.forms.profile_factory import UserProfileFormFactory
from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.views import AjaxViewMixin


class MyProfileDetailView(LoginRequiredMixin, DetailView):
    request: HttpRequest
    template_name = "accounts/user_profile/detail.html"

    def get_object(self, queryset=None):
        return self.request.user.profile_or_none


class MyProfileUpdateView(
    LoginRequiredMixin,
    AjaxViewMixin,
    HtmxFormViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    request: HttpRequest

    template_name = "accounts/user_profile/update.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_url = reverse_lazy("accounts:my-profile")
    success_message = _("Your profile has been updated.")

    extra_context = {"form_url": reverse_lazy("accounts:my-profile-update")}

    def get_object(self, queryset=None):
        return self.request.user.profile_or_none

    def get_form_class(self):
        return UserProfileFormFactory.for_user(user=self.request.user)

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "user": self.request.user,
            }
        )
        return initial


class ProfileFinishFormView(
    LoginRequiredMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    # form_class = UserProfileForm
    template_name = "accounts/user_profile/profile_finish.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"

    success_message = _("Your profile has been updated.")

    extra_context = {"form_url": reverse_lazy("accounts:profile-finish")}

    def get_form_class(self):
        return UserProfileFormFactory.for_user(
            user=self.request.user,
            base_form_class=UserProfileFinishForm,
        )

    def get_object(self, queryset=None):
        return self.request.user.profile_or_none

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "redirect_field_name": REDIRECT_FIELD_NAME,
                "redirect_field_value": get_next_redirect_url(self.request, REDIRECT_FIELD_NAME),
            }
        )
        return data

    def get_success_url(self):
        return get_next_redirect_url(self.request, REDIRECT_FIELD_NAME) or reverse("accounts:my-profile")

    def get_initial(self):
        initial = super().get_initial()
        initial.update(
            {
                "user": self.request.user,
            }
        )
        return initial
