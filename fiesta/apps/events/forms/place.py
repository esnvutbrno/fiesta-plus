from django.forms import CharField, HiddenInput, TextInput
from apps.events.models import Place
from apps.fiestaforms.forms import BaseModelForm
from django.utils.translation import gettext_lazy as _

class PlaceForm(BaseModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Place
        fields = (
            'name',
            'description',
            'link',
            "section",
            "map_link"
        )
        widgets = {
            "section": HiddenInput,

        }
