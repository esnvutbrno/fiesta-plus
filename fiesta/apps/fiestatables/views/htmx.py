from django.core.paginator import EmptyPage

from apps.sections.middleware.user_membership import HttpRequest
from apps.utils.views import AjaxViewMixin


class HtmxTableMixin(AjaxViewMixin):  # (TemplateView):
    request: HttpRequest
    ajax_template_name = "fiestatables/table.html"

    def get_context_data(self, **kwargs):
        try:
            return super().get_context_data(**kwargs)
        except EmptyPage:
            if self.request.GET.get("page"):
                ...
            ...
