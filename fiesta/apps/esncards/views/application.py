from django.views.generic import CreateView, FormView

from apps.accounts.models import UserProfile
from apps.esncards.forms.application import ESNcardApplicationForm
from apps.plugins.middleware.plugin import HttpRequest


class ESNcardApplicationCreateView(CreateView):
    request: HttpRequest

    form_class = ESNcardApplicationForm
    template_name = "esncards/application_create_form.html"

    def get_initial(self):
        profile: UserProfile = self.request.user.profile
        university = (
            profile.guest_faculty.university
            if profile.guest_faculty else
            profile.home_faculty.university
            if profile.home_faculty else
            profile.home_university
        )

        return dict(
            user=self.request.user,
            university=university,
            section=self.request.membership.section,

            first_name=self.request.user.first_name,
            last_name=self.request.user.last_name,
            nationality=profile.nationality,
        )
