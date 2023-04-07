from _operator import attrgetter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.forms import HiddenInput
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, TemplateView, DetailView

from apps.fiestaforms.forms import BaseModelForm
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.section_space import EnsureNotInSectionSpaceViewMixin
from apps.utils.breadcrumbs import BreadcrumbItem, with_object_breadcrumb


class NewSectionMembershipForm(BaseModelForm):
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

    def clean_role(self):
        if (role := self.cleaned_data["role"]) not in (
            SectionMembership.Role.MEMBER,
            SectionMembership.Role.INTERNATIONAL,
        ):
            raise ValidationError(
                _("You can request only for member or international role.")
            )
        return role


class MyMembershipsView(TemplateView):
    template_name = "accounts/memberships/my_memberships.html"


class NewSectionMembershipFormView(
    LoginRequiredMixin,
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
        form.instance.state = SectionMembership.State.UNCONFIRMED
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
