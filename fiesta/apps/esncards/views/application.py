from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView

from apps.accounts.models import User, UserProfile
from apps.esncards.forms.application import ESNcardApplicationForm
from apps.esncards.models import ESNcardApplication
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.files.utils import copy_between_storages
from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.membership import UserPassesMembershipTestMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class ApplicationCreateView(
    EnsureInSectionSpaceViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    CreateView,
):
    request: HttpRequest
    object: ESNcardApplication

    form_class = ESNcardApplicationForm
    template_name = "esncards/application_create.html"
    success_message = _("Application has been created.")
    permission_denied_message = _("An ESNcard application for current user for this section already exists.")

    def test_membership(self, membership: SectionMembership) -> bool:
        return membership.user.esncard_applications.filter(section=membership.section).exists()

    def get_initial(self):
        profile: UserProfile = self.request.user.profile_or_none
        university = (profile.faculty.university if profile.faculty else profile.university) if profile else None

        return dict(
            user=self.request.user,
            university=university,
            section=self.request.membership.section,
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
            nationality=profile.nationality if profile else None,
        )

    def form_valid(self, form):
        resp = super().form_valid(form)

        user: User = self.request.user

        # application is submitted, so great time to set the user
        # details, if he doesn't have them
        user.first_name = user.first_name or self.object.first_name
        user.last_name = user.last_name or self.object.last_name
        user.save(update_fields=["first_name", "last_name"])

        if profile := user.profile_or_none:
            # same with profile information and user picture
            profile.nationality = profile.nationality or self.object.nationality
            profile.picture = profile.picture or copy_between_storages(
                from_=self.object.holder_photo,
                to_=profile.picture,
                to_instance=profile,
            )
            profile.save(update_fields=["nationality", "picture"])

        return resp

    def get_template_names(self):
        return ["esncards/application_create_form.html"] if self.request.htmx else ["esncards/application_create.html"]

    def get_success_url(self):
        return reverse("esncards:application_detail", kwargs=dict(pk=self.object.pk))


class ApplicationDetailView(UserPassesMembershipTestMixin, DetailView):
    # TODO: check perms
    request: HttpRequest
    object: ESNcardApplication

    template_name = "esncards/application_detail.html"
    queryset = ESNcardApplication.objects.all()

    def test_membership(self, membership: SectionMembership) -> bool:
        self.object = self.get_object(queryset=self.queryset or self.get_queryset())
        return membership.is_privileged or membership.user == self.object.user
