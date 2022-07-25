from django.forms import HiddenInput
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from apps.fiestaforms.forms import BaseModelForm
from apps.sections.models import SectionMembership


class NewSectionMembershipForm(BaseModelForm):
    # TODO: clean role only to member/international

    submit_text = _("Request for membership")

    class Meta:
        model = SectionMembership
        fields = (
            "section",
            "user",  # to keep the validation unique together
            "role",
        )
        widgets = {
            "role": HiddenInput,
            "user": HiddenInput,
        }


class MembershipView(TemplateView):
    template_name = "accounts/membership.html"


class NewSectionMembershipFormView(CreateView):
    template_name = "accounts/new_membership.html"
    form_class = NewSectionMembershipForm

    def get_success_url(self):
        return reverse("accounts:membership")

    def form_valid(self, form):
        # override to be sure
        form.instance.user = self.request.user
        form.instance.state = SectionMembership.State.INACTIVE
        return super().form_valid(form)

    def get_initial(self):
        return {
            "role": SectionMembership.Role.INTERNATIONAL,
            "user": self.request.user,
        }
