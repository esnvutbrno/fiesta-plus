from django.forms import CharField, HiddenInput
from apps.events.models import PriceVariant
from apps.fiestaforms.forms import BaseModelForm

class PriceForm(BaseModelForm):
    class Meta:
        model = PriceVariant
        fields = (
            # TODO: place ?
            'title',
            'type',
            'amount',
            'event',
            'available_from',
            'available_to',
            'data'
        )
        widgets = {
            "event": HiddenInput,
        }
