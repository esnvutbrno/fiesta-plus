
from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Organizer
from apps.accounts.models import User
from django.forms import CharField, HiddenInput, MultipleChoiceField, ModelMultipleChoiceField, Select
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
    
    role = Select(choices=Organizer.Role.choices)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    

    def save(self, commit=True):
        organizers = self.cleaned_data["add_organizer"]
        event = self.cleaned_data["event"]
        role = self.cleaned_data['role']	

        for organizer in organizers:
            Organizer.objects.get_or_create(
                event=event,
                user=organizer,
                role=role
            )

        return 

    class Meta:
        model = Organizer
        fields = (
            "add_organizer",
            "role",
            "event"
        )
        widgets = {
            "event": HiddenInput,
        }
        