from allauth.account.utils import get_next_redirect_url
from allauth.utils import get_request_param
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, UpdateView

from apps.accounts.forms.profile_finish import UserProfileForm
from apps.accounts.models import AccountsConfiguration, UserProfile
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.views import PluginConfigurationViewMixin
from apps.utils.breadcrumbs import with_breadcrumb


@with_breadcrumb(_("My Profile"))
class MyProfileView(TemplateView):
    template_name = "accounts/my_profile.html"


@with_breadcrumb(_("Finish my profile"))
class ProfileFinishFormView(
    HtmxFormMixin,
    SuccessMessageMixin,
    PluginConfigurationViewMixin[AccountsConfiguration],
    UpdateView,
):
    form_class = UserProfileForm
    template_name = "accounts/user_profile/profile_finish.html"
    success_message = _("Your profile has been updated.")

    def get_object(self, queryset=None):
        try:
            return self.request.user.profile
        except UserProfile.DoesNotExist:
            return None

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "redirect_field_name": REDIRECT_FIELD_NAME,
                "redirect_field_value": get_request_param(
                    self.request, REDIRECT_FIELD_NAME
                ),
            }
        )
        return data

    def get_template_names(self):
        # TODO: mixin?
        return (
            ["accounts/user_profile/profile_finish_form.html"]
            if self.request.htmx
            else ["accounts/user_profile/profile_finish.html"]
        )

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return get_next_redirect_url(self.request, REDIRECT_FIELD_NAME)

    def get_form_class(self):
        return UserProfileForm.for_user(user=self.request.user)
