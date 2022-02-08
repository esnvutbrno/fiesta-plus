from django.forms import CharField, HiddenInput, ImageField
from django.utils.translation import gettext_lazy as _

from apps.esncards.models import ESNcardApplication
from apps.fiestaforms.forms import BaseModelForm, DateInput


class ESNcardApplicationForm(BaseModelForm):
    title = _("Application Form")

    photo = ImageField(
        label=_("Holder photo"),
        required=False,
        help_text=_("Front passport-sized photo is needed."),
    )

    university_name = CharField(label=_("Studies at"), disabled=True)
    section_name = CharField(label=_("ESN section"), disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields['first_name'].disabled = True
        # self.fields['last_name'].disabled = True
        # self.fields['nationality'].disabled = True
        self.fields["section"].disabled = True
        self.fields["university"].disabled = True

        self.initial["section_name"] = self.initial["section"].name
        self.initial["university_name"] = self.initial["university"].name

    class Meta:
        model = ESNcardApplication
        fields = (
            "first_name",
            "last_name",
            "nationality",
            "birth_date",
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
