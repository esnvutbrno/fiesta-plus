from __future__ import annotations

from allauth.account.views import SignupView
from django.contrib import messages
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.db import transaction
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.accounts.models import UserProfile
from apps.buddy_system.forms import NewBuddyRequestForm
from apps.buddy_system.models import BuddySystemConfiguration
from apps.fiestarequests.views.request import BaseNewRequestView
from apps.plugins.views import PluginConfigurationViewMixin
from apps.sections.models import SectionMembership, SectionsConfiguration
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class BuddySystemEntrance(EnsureInSectionSpaceViewMixin, PluginConfigurationViewMixin, TemplateView):
    def get(self, request, *args, **kwargs):
        if self.request.membership.is_international:
            return HttpResponseRedirect(reverse("buddy_system:new-request"))

        c: BuddySystemConfiguration = self.configuration
        if c.matching_policy_instance.can_member_match:
            return HttpResponseRedirect(reverse("buddy_system:matching-requests"))

        return HttpResponseRedirect(reverse("buddy_system:index"))


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


class NewBuddyRequestView(BaseNewRequestView):
    form_class = NewBuddyRequestForm
    success_message = _("Your buddy request has been successfully created!")

    success_url = reverse_lazy("buddy_system:index")

    def get_initial(self):
        i = super().get_initial()
        p: UserProfile = self.request.user.profile_or_none
        return i | {
            "interests": p.interests if p else None,
        }
