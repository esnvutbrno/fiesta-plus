from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event
from django.forms import Field as FormField, modelform_factory, CharField, HiddenInput
from django.utils.translation import gettext_lazy as _

class AddEventForm(BaseModelForm):
    section_name = CharField(label=_("ESN section"), disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["section"].disabled = True

        self.initial["section_name"] = self.initial["section"].name

    class Meta:
        model = Event
        fields = (
            # TODO: place ?
            "title",
            "subtitle",
            "description",
            "capacity",
            "state",
            "start",
            "end",
            "landscape_cover",
            "portrait_cover",
            "section",
        )
        widgets = {
            "section": HiddenInput,
        }

