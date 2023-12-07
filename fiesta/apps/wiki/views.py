from __future__ import annotations

from django.http import HttpResponsePermanentRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from .adapter import wiki_adapter
from apps.utils.breadcrumbs import with_breadcrumb


@with_breadcrumb(_("Docs"), url_name="wiki:index")
class SearchWikiView(TemplateView):
    template_name = "wiki/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get("q")

        ctx["results"] = wiki_adapter.search(term=q) if q else []
        ctx["q"] = q

        self.request.titles.append(_("Search: {}").format(q))

        return ctx


@with_breadcrumb(_("Docs"), url_name="wiki:index")
class WikiView(TemplateView):
    template_name = "wiki/index.html"

    path: str

    def get(self, request, *args, **kwargs):
        self.path = self.kwargs.get("path") or "/"

        base, file_name = wiki_adapter.split_path(self.path)

        if file_name.startswith("_"):
            return HttpResponsePermanentRedirect(
                reverse("wiki:page", kwargs=dict(path=base)) if base else reverse("wiki:index")
            )
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        ctx["sidebar"], ctx["footer"] = wiki_adapter.get_page_parts(path=self.path)
        page = wiki_adapter.page_for_path(path=self.path)
        ctx["page"] = page
        self.request.titles.append(page.get("title"))

        return ctx
