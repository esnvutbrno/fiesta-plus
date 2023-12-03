from apps.events.models.organizer import OrganizerRole
from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event, Organizer
from apps.accounts.models import User
from django.forms import CharField, HiddenInput, MultipleChoiceField, ModelMultipleChoiceField, SelectMultiple, SelectMultiple, Field, Select
from django_select2.forms import Select2MultipleWidget
from django.utils.translation import gettext_lazy as _
from apps.fiestaforms.widgets.models import MultipleActiveLocalMembersFromSectionWidget, PlaceWidget



class OrganizerForm(BaseModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
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
        organizers = self.cleaned_data["add_organizer"]
        mocs = self.cleaned_data["add_main_organizer"]
        event = self.cleaned_data["event"]	

        for organizer in organizers:
            if Organizer.objects.filter(event=event, user=organizer).exists():
                continue    
            Organizer.objects.update_or_create(
                event=event,
                user=organizer,
                state=OrganizerRole.OC
            )

        for moc in mocs:
            if Organizer.objects.filter(event=event, user=moc).exists() or moc in organizers:
                continue  
            Organizer.objects.update_or_create(
                event=event,
                user=moc,
                state=OrganizerRole.EVENT_LEADER
            )
        return 

    class Meta:
        model = Organizer
        fields = (
            "add_organizer",
            "event"
        )
        widgets = {
            "event": HiddenInput,
        }
        