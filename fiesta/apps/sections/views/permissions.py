from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils.translation import gettext_lazy as _

from apps.sections.middleware.section_space import HttpRequest
from apps.sections.models import SectionMembership


class UserIsPrivilegedInCurrentSectionMixin(UserPassesTestMixin):
    """
    View mixin checking wheever is logged user in privileged role (editor or admin)
    in current section space.
    """

    request: HttpRequest

    permission_denied_message = _("Page is restricted to privileged roles.")

    def test_func(self):
        membership = self.request.membership

        if self.request.user.is_superuser:
            # superuser can do anything
            if not self.request.htmx:
                messages.warning(self.request, _("Accesing as superuser, be aware!"))
            return True

        if not membership:
            # no membership? definitely no access
            return False

        if membership.section != self.request.in_space_of_section:
            # TODO: should not happen? is always True?
            #  !membership OR (membership.section==in_space_of_section)
            return False

        if not SectionMembership.Role(membership.role).is_privileged:
            # right section, but without sufficient role
            return False

        # TODO: check anything else?
        return True
