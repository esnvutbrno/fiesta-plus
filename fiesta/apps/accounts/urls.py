from django.urls import path

# Define your urls here
from django.views.generic import TemplateView


class MyView(TemplateView):
    template_name = "accounts/main.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        self.request.plugin.app_config.urls[0]

        return data


urlpatterns = [
    path("", TemplateView.as_view(template_name="accounts/main.html"), name="index"),
    path("test", MyView.as_view(), name="view"),
]
