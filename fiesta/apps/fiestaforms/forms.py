from __future__ import annotations

from django.forms import DateInput as DjDateInput, Form, Media, ModelForm
from django.utils.translation import gettext_lazy as _
from webpack_loader.utils import get_files


class DateInput(DjDateInput):
    input_type = "date"


class BaseModelForm(ModelForm):
    template_name = "fiestaforms/classic.html"
    submit_text: str = _("Save")

    @property
    def base_form_class(self):
        return BaseModelForm


class BaseForm(Form):
    template_name = "fiestaforms/classic.html"
    submit_text: str = _("Submit")

    @property
    def base_form_class(self):
        return BaseForm


class WebpackMediaFormMixin:
    _webpack_bundle: str

    @property
    def media(self):
        media = super().media
        media += Media(js=[f["url"] for f in get_files(self._webpack_bundle)])

        return media
