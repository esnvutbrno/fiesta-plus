from apps.events.models.organizer import OrganizerRole
from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event, Organizer
from apps.accounts.models import User
from django.forms import CharField, HiddenInput, MultipleChoiceField, ModelMultipleChoiceField, SelectMultiple, SelectMultiple
from django_select2.forms import Select2MultipleWidget
from django.utils.translation import gettext_lazy as _
from apps.fiestaforms.widgets.models import MultipleActiveLocalMembersFromSectionWidget

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
            "author"
        )
        widgets = {
            "section": HiddenInput,
            "author": HiddenInput,
        }


class UpdateEventForm(BaseModelForm):
    # section_name = CharField(label=_("ESN section"), disabled=True)
    # author_name = CharField(label=_("Author of the event"), disabled=True)

    add_organizer = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label=_("Add organizer"),
        widget=MultipleActiveLocalMembersFromSectionWidget,
        required=False
    )

    add_main_organizer = ModelMultipleChoiceField(
        queryset=User.objects.all(),
        label=_("Add event leader"),
        widget=MultipleActiveLocalMembersFromSectionWidget,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

    def save(self, commit=True):
        event = super().save(commit=commit)

        # # Getting the data doesnt work, TODO: fix
        organizers = self.cleaned_data["add_organizer"]
        mocs = self.cleaned_data["add_main_organizer"]

        # # # Create organizers for the selected users
        for organizer in organizers:
            Organizer.objects.update_or_create(
                event=event,
                user=organizer,
                state=OrganizerRole.OC
            )
            
        for moc in mocs:
                Organizer.objects.update_or_create(
                event=event,
                user=moc,
                state=OrganizerRole.EVENT_LEADER
            )
        return event

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
            "add_organizer"
        )
        widgets = {
            "section": HiddenInput,
            "author": HiddenInput,
        }

