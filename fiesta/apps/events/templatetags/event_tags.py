from __future__ import annotations

from django import template
from django.db.models import Q
from apps.events.models import Event
from apps.events.models.organizer import OrganizerRole
from apps.events.models.participant import ParticipantState
from apps.accounts.models import User
from apps.plugins.middleware.plugin import HttpRequest

register = template.Library()


@register.simple_tag(takes_context=True)
def show_participants(context, event: Event):
    request: HttpRequest = context["request"]

    if event.can_see_participants(request.membership.user):
        return event.participants.filter(state='confirmed')
    return None


@register.simple_tag
def get_ocs(event: Event):
    return event.organizers.all()


@register.simple_tag(takes_context=True)
def get_price_variants(context, event: Event):
    request: HttpRequest = context["request"]

    if request.membership.user.is_esn_card_holder or request.membership.role == 'admin':
        return event.price_variants.all()
    else:
        return event.price_variants.filter(Q(type='standard') | Q(type='free'))


@register.simple_tag(takes_context=True)
def testtag(context):
    print("testtag-----------------------------------")
    return "testtag-----------------------------------"

@register.simple_tag(takes_context=True)
def get_event_fullness(context, event: Event):
    if event.participants.all().count() <= event.capacity:
        return ("green","Registration opened")
    elif event.participants.all().count() > event.capacity:
        return ("yellow","Some spots left")
    elif event.participants.all().count() == event.capacity:
        return ("red", "Event is full")
    
@register.simple_tag(takes_context=True)
def is_oc(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.organizers.filter(user=request.membership.user).exists()

@register.simple_tag(takes_context=True)
def is_moc(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.organizers.filter(user=request.membership.user, role=OrganizerRole.EVENT_LEADER).exists()

@register.simple_tag(takes_context=True)
def is_participant(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return event.participants.filter(user=request.membership.user, role=ParticipantState.CONFIRMED).exists()

@register.simple_tag(takes_context=True)
def can_edit(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return is_moc(context, event) or event.author == request.membership.user or request.membership.user.is_superuser

@register.simple_tag(takes_context=True)
def can_see_participants(context, event: Event) -> bool:
    request: HttpRequest = context["request"]
    return is_moc(context, event) or event.author == request.membership.user or request.membership.user.is_superuser