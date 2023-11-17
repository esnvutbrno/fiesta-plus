from __future__ import annotations

from collections.abc import Callable

from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.forms import ModelForm
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView

from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class UpdateMembershipView(EnsureInSectionSpaceViewMixin, EnsurePrivilegedUserViewMixin, UpdateView):
    permission_denied_message = _("You've insufficient privileges to perform this action.")

    model = SectionMembership
    object: SectionMembership

    _check_membership_change: Callable[[ModelForm], None]

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        membership = self.request.membership
        if not (membership.is_section_admin or not self.object.is_privileged) and membership != self.object:
            return PermissionDenied(_("You've insufficient privileges to perform this action."))

        form = self.get_form()

        if form.is_valid():
            self._check_membership_change(form)
            return self.form_valid(form)

        return self.form_invalid(form)

    def get_queryset(self):
        return self.request.in_space_of_section.memberships

    def get_success_url(self):
        return reverse("sections:membership-detail", kwargs={"pk": self.object.pk})


class MembershipStateEditorView(
    SuccessMessageMixin,
    HtmxFormViewMixin,
    UpdateMembershipView,
):
    fields = ("state",)

    success_message = _("User state changed successfully.")

    def _check_membership_change(self, form):
        # new_state: SectionMembership.State = form.cleaned_data["state"]

        if not self.request.membership.is_section_admin and self.object.is_section_admin:
            raise PermissionDenied(_("You've insufficient privileges to perform this action."))

        if self.request.membership == self.object:
            raise PermissionDenied(_("You cannot change your own state."))


class MembershipRoleEditorView(
    SuccessMessageMixin,
    HtmxFormViewMixin,
    UpdateMembershipView,
):
    fields = ("role",)

    success_message = _("User role changed successfully.")

    def _check_membership_change(self, form):
        new_role: SectionMembership.Role = form.cleaned_data["role"]

        if not self.request.membership.is_section_admin and self.object.is_section_admin:
            raise PermissionDenied(_("You've insufficient privileges to perform this action."))

        if not self.request.membership.is_section_admin and new_role == SectionMembership.Role.ADMIN:
            raise PermissionDenied(_("You've insufficient privileges to perform this action."))

        if self.request.membership == self.object:
            raise PermissionDenied(_("You cannot change your own role."))
