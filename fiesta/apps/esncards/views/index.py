from django.views.generic import TemplateView


class EsncardsIndexView(TemplateView):
    template_name = "esncards/index.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["applications"] = self.request.user.esncard_applications.all()
        return ctx
