from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponse, HttpResponseNotFound

from ...utils.models.query import get_single_object_or_none
from ...utils.request import HttpRequest as BaseHttpRequest
from ..models import Section


class HttpRequest(BaseHttpRequest):
    in_space_of_section: Section | None


class SectionSpaceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        # xxx.fiestdomain.tld
        requested_host: str = request.get_host()
        site: Site = get_current_site(request=request)

        # 'xxx' or empty string
        space_slug = requested_host.removesuffix(site.domain).removesuffix(".")

        request.in_space_of_section = get_single_object_or_none(
            # optimization
            Section.objects.get_queryset().prefetch_related("plugins"),
            space_slug=space_slug,
        )

        if not space_slug or space_slug == settings.ROOT_DOMAIN:
            return self.get_response(request)

        if not request.in_space_of_section:
            return HttpResponseNotFound("Section space not found.")

        if request.in_space_of_section.system_state != Section.SystemState.ENABLED:
            return HttpResponseNotFound("Section is not enabled.")

        return self.get_response(request)


__all__ = ["SectionSpaceMiddleware", "HttpRequest"]
