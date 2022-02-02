from django.forms import ModelForm

from apps.esncards.models import ESNcardApplication


class ESNcardApplicationForm(ModelForm):
    template_name = "fiesta/forms/classic.html"

    class Meta:
        model = ESNcardApplication
        fields = (
            "first_name",
            "last_name",
            "nationality",
            "user",
            "section",
            "university",
        )
