from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext as _

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership


class UserPassesMembershipTestMixin(UserPassesTestMixin):
    request: HttpRequest

    def test_func(self):
        membership = self.request.membership

        if self.request.user.is_superuser:
            # superuser can do anything
            if not self.request.htmx:
                messages.warning(self.request, _("Accessing as superuser, be aware!"))
            return True

        if not membership:
            # no membership? definitely no access
            return False

        if membership.section != self.request.in_space_of_section:
            # TODO: should not happen? is always True?
            #  !membership OR (membership.section==in_space_of_section)
            return False

        if not self.test_membership(membership=membership):
            # right section, but without sufficient role
            return False

        return True

    def test_membership(self, membership: SectionMembership) -> bool:
        raise NotImplementedError("To be overriden")


class EnsureLocalUserViewMixin(UserPassesMembershipTestMixin):
    request: HttpRequest

    def test_membership(self, membership: SectionMembership) -> bool:
        return membership.is_local


class EnsureInternationalUserViewMixin(UserPassesMembershipTestMixin):
    request: HttpRequest

    def test_membership(self, membership: SectionMembership) -> bool:
        return membership.is_international


class EnsurePrivilegedUserViewMixin(UserPassesMembershipTestMixin):
    """
    View mixin checking wheever is logged user in privileged role (editor or admin)
    in current section space.
    """

    permission_denied_message = _("Page is restricted to privileged users.")

    def test_membership(self, membership: SectionMembership) -> bool:
        return membership.is_privileged
