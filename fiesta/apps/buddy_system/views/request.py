from allauth.account.views import SignupView
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView, CreateView

from apps.buddy_system.forms import NewBuddyRequestForm
from apps.sections.models import SectionMembership
from apps.sections.views.space_mixin import EnsureInSectionSpaceViewMixin


class WannaBuddyView(TemplateView):
    template_name = "buddy_system/wanna_buddy.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "continue_url": "?".join(
                    (
                        reverse("buddy_system:sign-up-before-request"),
                        urlencode(
                            {REDIRECT_FIELD_NAME: reverse("buddy_system:new-request")}
                        ),
                    )
                )
            }
        )
        return data


class SignUpBeforeRequestView(EnsureInSectionSpaceViewMixin, SignupView):
    template_name = "buddy_system/sign_up_before_request.html"

    success_url = reverse_lazy("buddy_system:new-request")

    def form_valid(self, form):
        response = super().form_valid(form)

        SectionMembership.objects.get_or_create(
            user=self.user,
            section=self.request.in_space_of_section,
            role=SectionMembership.Role.INTERNATIONAL,
            state=SectionMembership.State.ACTIVE,
        )

        return response


class NewRequestView(EnsureInSectionSpaceViewMixin, SuccessMessageMixin, CreateView):
    template_name = "buddy_system/new_buddy_request.html"
    form_class = NewBuddyRequestForm
    success_message = _("Your buddy request has been succesfully created!")

    success_url = reverse_lazy("buddy_system:index")

    def get_initial(self):
        return {
            "responsible_section": self.request.in_space_of_section,
            "issuer": self.request.user,
        }

    def form_valid(self, form):
        # override to be sure
        form.instance.responsible_section = self.request.in_space_of_section
        form.instance.issuer = self.request.user
        return super().form_valid(form)
