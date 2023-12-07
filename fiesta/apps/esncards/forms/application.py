from __future__ import annotations

from django.forms import CharField, HiddenInput
from django.utils.translation import gettext_lazy as _

from apps.esncards.models import ESNcardApplication
from apps.fiestaforms.forms import BaseModelForm, DateInput


class ESNcardApplicationForm(BaseModelForm):
    university_name = CharField(label=_("Studies at"), disabled=True)
    section_name = CharField(label=_("ESN section"), disabled=True)

    submit_text = _("Submit application")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["section"].disabled = True
        self.fields["university"].disabled = True

        self.initial["section_name"] = self.initial["section"].name
        self.initial["university_name"] = self.initial["university"].name if self.initial["university"] else None

    class Meta:
        model = ESNcardApplication
        fields = (
            "first_name",
            "last_name",
            "nationality",
            "birth_date",
            "holder_photo",
            "user",
            "section",
            "university",
        )
        widgets = {
            "birth_date": DateInput,
            "user": HiddenInput,
            "section": HiddenInput,
            "university": HiddenInput,
        }
