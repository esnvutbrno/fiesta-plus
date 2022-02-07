from django.forms import DateInput as DjDateInput, ModelForm


class DateInput(DjDateInput):
    input_type = 'date'


class BaseModelForm(ModelForm):
    template_name = "fiestaforms/classic.html"
    title: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_context(self):
        ctx: dict = super().get_context()

        return ctx
