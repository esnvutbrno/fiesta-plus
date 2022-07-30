from _operator import attrgetter

from django.forms import HiddenInput
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, DetailView

from apps.fiestaforms.forms import BaseModelForm
from apps.sections.models import SectionMembership
from apps.sections.views.space_mixin import EnsureNotInSectionSpaceViewMixin
from apps.utils.breadcrumbs import BreadcrumbItem, with_object_breadcrumb


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


class MyMembershipsView(TemplateView):
    template_name = "accounts/memberships/my_memberships.html"


class NewSectionMembershipFormView(
    EnsureNotInSectionSpaceViewMixin,
    CreateView,
):
    template_name = "accounts/memberships/new_membership.html"
    form_class = NewSectionMembershipForm

    extra_context = dict(
        parent_breadcrumb=BreadcrumbItem(
            _("My Memberships"), reverse_lazy("accounts:membership")
        )
    )

    def get_success_url(self):
        return reverse("accounts:membership")

    def form_valid(self, form):
        # override to be sure
        form.instance.user = self.request.user
        form.instance.state = SectionMembership.State.INACTIVE
        return super().form_valid(form)

    def get_form(self, form_class=None):
        form: NewSectionMembershipForm = super().get_form(form_class=form_class)

        if self.kwargs.get("section"):
            form.fields["section"].disabled = True

        return form

    def get_initial(self):
        return {
            "role": SectionMembership.Role.INTERNATIONAL,
            "user": self.request.user,
            "section": self.kwargs.get("section"),
        }


@with_object_breadcrumb(getter=attrgetter("user.full_name"))
class MembershipDetailView(DetailView):
    model = SectionMembership
    template_name = "accounts/user_detail/user_detail.html"
