from __future__ import annotations

from operator import itemgetter

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
    _common_bundle: str = "main"
    _bundle: str

    @property
    def media(self):
        media = super().media
        media += Media(
            js=tuple(
                set(map(itemgetter("url"), get_files(self._bundle)))
                # - set(map(itemgetter("url"), get_files(self._common_bundle)))
            )
        )

        return media
