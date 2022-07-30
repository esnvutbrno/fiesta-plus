from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from apps.accounts.forms.profile import UserProfileFinishForm, UserProfileForm
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.breadcrumbs import with_breadcrumb
from apps.utils.views import AjaxViewMixin


class MyProfileDetailView(UpdateView):
    request: HttpRequest
    template_name = "accounts/user_profile/update.html"

    def get_object(self, queryset=None):
        return self.request.user.profile_or_none

    def get_form_class(self):
        return UserProfileForm.for_user(user=self.request.user)


@with_breadcrumb(_("Finish my profile"))
class ProfileFinishFormView(
    HtmxFormMixin,
    AjaxViewMixin,
    SuccessMessageMixin,
    UpdateView,
):
    # form_class = UserProfileForm
    template_name = "accounts/user_profile/profile_finish.html"
    ajax_template_name = "accounts/user_profile/profile_form.html"

    success_message = _("Your profile has been updated.")

    def get_form_class(self):
        return UserProfileFinishForm.for_user(user=self.request.user)

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
                "redirect_field_value": get_next_redirect_url(
                    self.request, REDIRECT_FIELD_NAME
                ),
            }
        )
        return data

    def get_success_url(self):
        return get_next_redirect_url(self.request, REDIRECT_FIELD_NAME) or reverse(
            "accounts:my-profile"
        )
