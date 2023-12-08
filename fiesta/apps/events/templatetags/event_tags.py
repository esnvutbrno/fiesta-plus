from __future__ import annotations

from django import template
from django.db.models import Q
from apps.events.models import Event, Organizer, Participant
from apps.events.models.price_variant import EventPriceVariantType
from apps.plugins.middleware.plugin import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag(takes_context=True)
def show_participants(context, event: Event):
    request: HttpRequest = context["request"]

    if event.can_see_participants(request.membership.user):
        return event.participants.filter(state='confirmed')
    return None


@register.simple_tag(takes_context=True)
def get_price_variants(context, event: Event):
    request: HttpRequest = context["request"]

    if request.membership.user.is_esn_card_holder or request.membership.is_section_admin:
        return event.price_variants.all()
    else:
        return event.price_variants.filter(Q(type=EventPriceVariantType.STANDARD) | Q(type=EventPriceVariantType.FREE))

@register.simple_tag(takes_context=True)
def get_event_fullness(context, event: Event):  
    if Participant.objects.filter(event=event, state=Participant.State.CONFIRMED).count() < event.capacity/2:
        return mark_safe('<span class="bg-success p-2 rounded-full">Opened</span>')
    elif Participant.objects.filter(event=event, state=Participant.State.CONFIRMED).count() < event.capacity and Participant.objects.filter(event=event, state=Participant.State.CONFIRMED).count() >= event.capacity/2:
        return mark_safe('<span class="bg-warning p-2  rounded-full">Almost full</span>')
    elif Participant.objects.filter(event=event, state=Participant.State.CONFIRMED).count() >= event.capacity:
        return mark_safe('<span class="bg-error p-2  rounded-full">Full</span>')
    
@register.simple_tag(takes_context=True)
def is_oc(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.event_organizers.filter(user=request.membership.user).exists()

@register.simple_tag(takes_context=True)
def is_moc(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.event_organizers.filter(user=request.membership.user, role=Organizer.Role.EVENT_LEADER).exists()

@register.simple_tag(takes_context=True)
def is_participant(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.participants.filter(user=request.membership.user, role=Participant.State.CONFIRMED).exists()

@register.simple_tag(takes_context=True)
def can_edit(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return is_moc(context, event) or event.author == request.membership.user or request.membership.is_privileged or request.membership.user.has_perm('events.change_event')

@register.simple_tag(takes_context=True)
def can_see_participants(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return is_moc(context, event) or event.author == request.membership.user or request.membership.is_privileged or request.membership.user.has_perm('events.change_event')

