from django.views.generic import TemplateView


class EsncardsIndexView(TemplateView):
    template_name = "esncards/index.html"
