from django.forms import HiddenInput, DateTimeInput
from apps.events.models import PriceVariant
from apps.fiestaforms.forms import BaseModelForm

class PriceForm(BaseModelForm):
    class Meta:
        model = PriceVariant
        fields = (
            'title',
            'type',
            'amount',
            'event',
            'available_from',
            'available_to',
        )
        widgets = {
            "event": HiddenInput,
            "avilable_from": DateTimeInput(attrs={'type': 'datetime-local'}),
            "avilable_to": DateTimeInput(attrs={'type': 'datetime-local'}),
        }
