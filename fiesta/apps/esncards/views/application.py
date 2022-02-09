from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import CreateView, DetailView

from apps.accounts.models import UserProfile
from apps.esncards.forms.application import ESNcardApplicationForm
from apps.esncards.models import ESNcardApplication
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.plugins.middleware.plugin import HttpRequest
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb


@with_breadcrumb(_("New Application"))
class ApplicationCreateView(SuccessMessageMixin, HtmxFormMixin, CreateView):
    request: HttpRequest

    form_class = ESNcardApplicationForm
    template_name = "esncards/application_create.html"
    success_message = _('Application has been created.')

    def get_initial(self):
        profile: UserProfile = self.request.user.profile
        university = (
            profile.guest_faculty.university
            if profile.guest_faculty
            else profile.home_faculty.university
            if profile.home_faculty
            else profile.home_university
        )

        return dict(
            user=self.request.user,
            university=university,
            section=self.request.membership.section,
            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
            nationality=profile.nationality,
        )

    def get_template_names(self):
        return (
            ["esncards/application_create_form.html"]
            if self.request.htmx
            else ["esncards/application_create.html"]
        )

    def get_success_url(self):
        return reverse("esncards:detail-application", kwargs=dict(pk=self.object.pk))


@with_object_breadcrumb()
class ApplicationDetailView(DetailView):
    request: HttpRequest

    template_name = "esncards/application_detail.html"
    queryset = ESNcardApplication.objects.all()
