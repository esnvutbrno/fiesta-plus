from django.utils.translation import gettext_lazy as _
from django.views.generic import TemplateView

from apps.utils.breadcrumbs import with_breadcrumb
from .elastic import wiki_elastic


@with_breadcrumb(_("Docs"), url_name="wiki:index")
class SearchWikiView(TemplateView):
    template_name = "wiki/search.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')

        ctx['results'] = wiki_elastic.search(term=q) if q else []
        ctx["q"] = q

        self.request.titles.append(_("Search: {}").format(q))

        return ctx


@with_breadcrumb(_("Docs"), url_name="wiki:index")
class WikiView(TemplateView):
    template_name = "wiki/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        path = self.kwargs.get("path") or '/'

        ctx["sidebar"], ctx["footer"] = wiki_elastic.get_page_parts(path=path)

        page = wiki_elastic.page_for_path(path=path)
        ctx["page"] = page
        self.request.titles.append(page.get("title"))

        return ctx
