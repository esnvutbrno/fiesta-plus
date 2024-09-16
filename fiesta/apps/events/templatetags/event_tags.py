from __future__ import annotations

from django import template
from django.db.models import Q
from apps.events.models import Event
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

    if request.membership.user.is_esn_card_holder:
        return event.price_variants.all()
    else:
        return event.price_variants.filter(Q(type='standard') | Q(type='free'))


@register.simple_tag(takes_context=True)
def testtag(context):
    print("testtag-----------------------------------")
    return "testtag-----------------------------------"
