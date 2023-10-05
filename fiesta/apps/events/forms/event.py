from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event, Organizer
from django.forms import Field as FormField, modelform_factory, CharField, HiddenInput, ChoiceField
from django.utils.translation import gettext_lazy as _

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
    memberships_queryset = SectionMembership.objects.all()
    membership_choices = [(membership.user.id, membership.user.full_name_official) for membership in memberships_queryset]

    add_organizer = ChoiceField(choices=membership_choices, label=_("Add organizer"), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # self.fields["section"].disabled = True
        # self.fields["author"].disabled = True

        # self.initial["section_name"] = self.initial["section"].name
        # self.initial["author_name"] = self.initial["author"].full_name

    
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
