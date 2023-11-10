from __future__ import annotations

from collections import namedtuple

from allauth.account.utils import get_next_redirect_url
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.http import urlencode
from django.views.generic import TemplateView

from apps.plugins.middleware.plugin import HttpRequest
from apps.sections.models import Section


class ChooseSpaceView(TemplateView):
    request: HttpRequest

    template_name = "sections/choose_space.html"

    def get(self, request, *args, **kwargs):
        # TODO: temporary hack, have to decide if need to have choosespace page
        next_url = get_next_redirect_url(self.request, REDIRECT_FIELD_NAME) or ""
        return HttpResponseRedirect(reverse("accounts:membership") + "?" + urlencode({REDIRECT_FIELD_NAME: next_url}))
        # maybe we are already in section space accidentally

        if self.request.in_space_of_section:
            return HttpResponseRedirect(self.request.build_absolute_uri(next_url))

        if self.request.all_memberships.count() == 1:
            only_section: Section = self.request.all_memberships.get().section

            return HttpResponseRedirect(only_section.section_base_url(self.request) + next_url)

        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        next_url = get_next_redirect_url(self.request, REDIRECT_FIELD_NAME) or ""

        SectionSpec = namedtuple("SectionSpec", "name url")
        data.update(
            {
                "sections": [
                    SectionSpec(s.name, s.section_base_url(self.request) + next_url)
                    # TODO: limit to current membership
                    for s in Section.objects.all()
                ]
            }
        )
        return data
