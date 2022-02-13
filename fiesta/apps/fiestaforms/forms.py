from django.forms import DateInput as DjDateInput, ModelForm


class DateInput(DjDateInput):
    input_type = "date"


class BaseModelForm(ModelForm):
    template_name = "fiestaforms/classic.html"
    title: str
