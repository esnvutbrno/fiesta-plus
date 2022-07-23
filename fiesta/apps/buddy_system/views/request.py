from allauth.account.views import SignupView
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.urls import reverse_lazy, reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView, CreateView

from apps.buddy_system.forms import NewBuddyRequestForm
from apps.sections.models import SectionMembership


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


class SignUpBeforeRequestView(SignupView):
    template_name = "buddy_system/sign_up_before_request.html"

    success_url = reverse_lazy("buddy_system:new-request")

    def form_valid(self, form):
        response = super().form_valid(form)

        # TODO: check existence of in_space_of_section, since without section it doesn't make sense
        SectionMembership.objects.get_or_create(
            user=self.user,
            section=self.request.in_space_of_section,
            role=SectionMembership.Role.INTERNATIONAL,
            state=SectionMembership.State.ACTIVE,
        )

        return response


class NewRequestView(CreateView):
    template_name = "buddy_system/new_request.html"
    form_class = NewBuddyRequestForm
