
from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event, Organizer
from apps.accounts.models import User
from django.forms import CharField, HiddenInput, DateTimeInput
from django_select2.forms import Select2MultipleWidget
from django.utils.translation import gettext_lazy as _
from apps.fiestaforms.widgets.models import MultipleActiveLocalMembersFromSectionWidget, PlaceWidget

from apps.sections.models import SectionMembership


class AddEventForm(BaseModelForm):
    section_name = CharField(label=_("ESN section"), disabled=True)
    author_name = CharField(label=_("Author of the event"), disabled=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["section"].disabled = True
        self.fields["author"].disabled = True

        self.initial["section_name"] = self.initial["section"].name
        self.initial["author_name"] = self.initial["author"].full_name


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
            "author",
            "place"
        )
        widgets = {
            "section": HiddenInput,
            "author": HiddenInput,
            "place": PlaceWidget,
            "start": DateTimeInput(attrs={'type': 'datetime-local'}),
            "end": DateTimeInput(attrs={'type': 'datetime-local'}),
        }

