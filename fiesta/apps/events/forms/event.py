from apps.events.models.organizer import OrganizerRole
from apps.fiestaforms.forms import BaseModelForm
from apps.events.models import Event, Organizer
from django.forms import CharField, HiddenInput, MultipleChoiceField, ModelMultipleChoiceField
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

    add_organizer = CharField(label=_("Add organizer"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        memberships_queryset = self.initial["section"].memberships.all()
        membership_choices = [(str(membership.user.id), membership.user.full_name_official) for membership in
                              memberships_queryset]

        self.fields["add_organizer"].queryset = membership_choices

    def save(self, commit=True):
        event = super().save(commit=commit)

        # Get the selected organizer user IDs from cleaned_data
        organizer_user_ids = self.cleaned_data.get("add_organizer", [])

        # Create organizers for the selected users
        for user_id in organizer_user_ids:
            Organizer.objects.create(
                user_id=user_id,
                event=event,
                state=OrganizerRole.OC,
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

