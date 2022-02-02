from apps.esncards.models import ESNcardApplication
from apps.fiestaforms.forms import BaseModelForm


class ESNcardApplicationForm(BaseModelForm):
    template_name = "fiestaforms/classic.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['first_name'].disabled = True
        self.fields['last_name'].disabled = True
        self.fields['nationality'].disabled = True

    class Meta:
        model = ESNcardApplication
        fields = (
            "first_name",
            "last_name",
            "nationality",
            # "user",
            # "section",
            # "university",
        )
        widgets = {
            # 'user': HiddenInput,
            # 'section': HiddenInput,
            # 'university': HiddenInput,
        }
