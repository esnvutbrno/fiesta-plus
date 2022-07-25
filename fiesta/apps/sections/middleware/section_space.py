from __future__ import annotations

from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse

from ..models import Section
from ...plugins.middleware.plugin import HttpRequest as HttpRequestOrig
from ...utils.models.query import get_object_or_none


class HttpRequest(HttpRequestOrig):
    in_space_of_section: Section | None


class SectionSpaceMiddleware:
    MEMBERSHIP_URL_NAME = "accounts:membership"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequestOrig) -> HttpResponse:
        # xxx.fiestdomain.tld
        requested_host: str = request.get_host()
        site: Site = get_current_site(request=request)

        # xxx or empty
        space_slug = requested_host.removesuffix(site.domain).removesuffix(".")

        request.in_space_of_section = get_object_or_none(Section, space_slug=space_slug)

        return self.get_response(request)


__all__ = ["SectionSpaceMiddleware", "HttpRequest"]
