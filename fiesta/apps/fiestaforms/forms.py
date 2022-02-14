from django.forms import DateInput as DjDateInput, ModelForm
from django.utils.translation import gettext_lazy as _


class DateInput(DjDateInput):
    input_type = "date"


class BaseModelForm(ModelForm):
    template_name = "fiestaforms/classic.html"
    title: str
    submit_text: str = _("Submit")
