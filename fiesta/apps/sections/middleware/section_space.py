from __future__ import annotations

from django.conf import settings
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.http import Http404, HttpResponse
from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from ...utils.models.query import get_single_object_or_none
from ...utils.request import HttpRequest as BaseHttpRequest
from ..models import Section


class HttpRequest(BaseHttpRequest):
    in_space_of_section: Section | None


class SectionSpaceMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        requested_host: str = request.get_host()
        site: Site = get_current_site(request=request)
        space_slug = requested_host.removesuffix(site.domain).removesuffix(".")

        cache_key = f"section_space_{space_slug}"
        section = cache.get(cache_key)
        
        print(section)
        if section is None:
            print("Heheheh")
            section = get_single_object_or_none(
                Section.objects.prefetch_plugins(),
                space_slug=space_slug,
            )
            cache.set(cache_key, section)

        request.in_space_of_section = section

        if not space_slug or space_slug == settings.ROOT_DOMAIN:
            return self.get_response(request)

        if not request.in_space_of_section:
            raise Http404("Section space not found.")

        return self.get_response(request)

@receiver(post_save, sender=Section)
@receiver(post_delete, sender=Section)
def invalidate_section_cache(sender, instance, **kwargs):
    print("cache invalidation")
    cache_key = f"section_space_{instance.space_slug}"
    cache.delete(cache_key)

__all__ = ["SectionSpaceMiddleware", "HttpRequest"]
