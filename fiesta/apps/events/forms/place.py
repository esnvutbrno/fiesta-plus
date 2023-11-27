from django.forms import CharField, HiddenInput
from apps.events.models import Place
from apps.fiestaforms.forms import BaseModelForm

class PlaceForm(BaseModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    class Meta:
        model = Place
        fields = (
            'name',
            'description',
            'link',
            'map_link',
            "section"
        )
        widgets = {
            "section": HiddenInput,
        }
