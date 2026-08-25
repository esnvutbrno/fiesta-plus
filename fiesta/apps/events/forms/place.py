from django.forms import CharField, HiddenInput, TextInput
from apps.events.models import Place
from apps.fiestaforms.forms import BaseModelForm
from django.utils.translation import gettext_lazy as _

class PlaceForm(BaseModelForm):
    def save(self, commit=True):
        instance = super().save(commit=False)
        map_url = self.cleaned_data.get('map_link')
        if map_url:
            instance.set_coordinates_from_url(map_url)

        instance.save()
        return instance
    
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
            "latitude": HiddenInput,
            "longitude": HiddenInput,
        }

