from django.core.paginator import EmptyPage


class HtmxTableMixin:  # (TemplateView):
    htmx_template_name = "fiestatables/table.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_template_names(self):
        if self.request.htmx:
            return [self.htmx_template_name]

        return super().get_template_names()

    def get_context_data(self, **kwargs):
        try:
            return super().get_context_data(**kwargs)
        except EmptyPage:
            if self.request.GET.get("page"):
                ...
            ...
