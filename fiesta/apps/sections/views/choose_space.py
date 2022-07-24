from collections import namedtuple

from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.views.generic import TemplateView

from apps.sections.models import Section


class ChooseSpaceView(TemplateView):
    template_name = "sections/choose_space.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        next_url = get_next_redirect_url(self.request, REDIRECT_FIELD_NAME) or ""

        SectionSpec = namedtuple("SectionSpec", "name url")
        data.update(
            {
                "sections": [
                    SectionSpec(s.name, s.section_url(self.request) + next_url)
                    for s in Section.objects.all()
                ]
            }
        )
        return data
