from apps.fiestaforms.forms import BaseForm


class BaseFilterForm(BaseForm):
    template_name = "fiestatables/filter_form.html"
    title: str
    submit_text: str = None

    @property
    def base_form_class(self):
        return BaseFilterForm
