from django.core.exceptions import ValidationError
from django.utils import timezone
from apps.events.models.participant import Participant
from apps.events.models.price_variant import PriceVariant, EventPriceVariantType

class ParticipantValidator:
    
    def get_price(self, event, user):
        if PriceVariant.objects.filter(event=event, type=EventPriceVariantType.FREE).exists():
            return PriceVariant.objects.filter(event=event, type=EventPriceVariantType.FREE).get()
        elif user.is_esn_card_holder and PriceVariant.objects.filter(event=event, type=EventPriceVariantType.WITH_ESN_CARD).exists():
            return PriceVariant.objects.filter(event=event, type=EventPriceVariantType.WITH_ESN_CARD).get()
        elif PriceVariant.objects.filter(event=event, type=EventPriceVariantType.STANDARD).exists():
            return PriceVariant.objects.filter(event=event, type=EventPriceVariantType.STANDARD).get()
        return None
    
    def register_for_event(self, user, event):
        """
        Method to validate registration for an event.
        """

        if Participant.objects.filter(event=event, state=Participant.State.CONFIRMED).count() >= event.capacity:
            raise ValidationError("This event is full.")

        if Participant.objects.filter(user=user, event=event).exists():
            raise ValidationError("You are already registered for this event.")
        price = self.get_price(event, user)
        if price is None:
            raise ValidationError("You can't register for this event yet.")

        return price