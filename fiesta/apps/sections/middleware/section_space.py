from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseNotFound

from ..models import Section
from ...utils.models.query import get_object_or_none
from ...utils.request import HttpRequest as BaseHttpRequest


class HttpRequest(BaseHttpRequest):
    in_space_of_section: Section | None


class SectionSpaceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: BaseHttpRequest) -> HttpResponse:
        # xxx.fiestdomain.tld
        requested_host: str = request.get_host()
        site: Site = get_current_site(request=request)

        # 'xxx' or empty string
        space_slug = requested_host.removesuffix(site.domain).removesuffix(".")

        request.in_space_of_section = get_object_or_none(Section, space_slug=space_slug)

        # TODO: detect active state of selected section

        if space_slug and space_slug != settings.ROOT_DOMAIN and not request.in_space_of_section:
            return HttpResponseNotFound("Section space not found.")

        return self.get_response(request)


__all__ = ["SectionSpaceMiddleware", "HttpRequest"]
