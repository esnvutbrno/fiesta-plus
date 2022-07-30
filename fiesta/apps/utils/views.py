from apps.utils.request import HttpRequest


class AjaxViewMixin:  # (TemplateView):
    request: HttpRequest
    ajax_template_name = None

    def get_template_names(self):
        if self.request.htmx or any(
            [
                self.request.META.get("HTTP_X_REQUESTED_WITH") == "XMLHttpRequest",
                self.request.content_type == "application/json",
                self.request.META.get("HTTP_ACCEPT") == "application/json",
            ]
        ):
            return [self.ajax_template_name]

        return super().get_template_names()

    def get_ajax_template_names(self):
        return [self.ajax_template_name]
