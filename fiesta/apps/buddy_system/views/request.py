from __future__ import annotations

from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.messages.views import SuccessMessageMixin
from django.db import transaction
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView

from apps.buddy_system.forms import NewBuddyRequestForm
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.models import SectionMembership, SectionsConfiguration
from apps.sections.views.mixins.membership import EnsureInternationalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class BuddySystemEntrance(EnsureInSectionSpaceViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.membership.is_international:
            return HttpResponseRedirect(reverse("buddy_system:new-request"))

        if self.request.membership.is_local:
            return HttpResponseRedirect(reverse("buddy_system:matching-requests"))

        raise Http404(_("Nothing to see here"))


class WannaBuddyView(EnsureInSectionSpaceViewMixin, TemplateView):
    template_name = "buddy_system/wanna_buddy.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "continue_url": (
                    "?".join(
                        (
                            reverse("buddy_system:sign-up-before-request"),
                            urlencode({REDIRECT_FIELD_NAME: reverse("buddy_system:entrance")}),
                        )
                    )
                    if not self.request.membership
                    else reverse("buddy_system:entrance")
                )
            }
        )
        return data


class SignUpBeforeEntranceView(
    EnsureInSectionSpaceViewMixin,
    PluginConfigurationViewMixin[SectionsConfiguration],
    SignupView,
):
    template_name = "buddy_system/sign_up_before_entrance.html"

    success_url = reverse_lazy("buddy_system:entrance")

    @property
    def configuration(self) -> SectionsConfiguration:
        """We cannot use PluginConfigurationViewMixin, since memberships is not ready and request.plugin is
        filled by middleware based on membership (and that's created in form_valid, so too late)."""
        return SectionsConfiguration.objects.filter(plugins__section=self.request.in_space_of_section).first()

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)

        if self.configuration.auto_approved_membership_for_international:
            state = SectionMembership.State.ACTIVE
            messages.success(self.request, _("Your now connected to the section."))
        else:
            state = SectionMembership.State.UNCONFIRMED
            messages.info(
                self.request,
                _("Your membership is now waiting for approval, you will be informed by e-mail."),
            )

        SectionMembership.objects.create(
            user=self.user,
            section=self.request.in_space_of_section,
            role=SectionMembership.Role.INTERNATIONAL,
            state=state,
        )

        return response


class NewRequestView(
    EnsureInSectionSpaceViewMixin,
    EnsureInternationalUserViewMixin,
    SuccessMessageMixin,
    CreateView,
):
    template_name = "buddy_system/new_buddy_request.html"
    form_class = NewBuddyRequestForm
    success_message = _("Your buddy request has been successfully created!")

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
