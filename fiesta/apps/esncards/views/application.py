from django.views.generic import CreateView, FormView

from apps.esncards.forms.application import ESNcardApplicationForm


class ESNcardApplicationCreateView(CreateView):
    form_class = ESNcardApplicationForm
    template_name = "esncards/application_create_form.html"
