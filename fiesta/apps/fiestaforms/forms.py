from crispy_forms.helper import FormHelper
from django.forms import ModelForm


class BaseModelForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
