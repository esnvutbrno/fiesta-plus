from __future__ import annotations

import re

from django import template

from apps.pickup_system.apps import PickupSystemConfig
from apps.pickup_system.models import PickupRequest
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugins_mapped_to_class

register = template.Library()

# I know, it's not the best regex for emails
# [\w.] as [a-zA-Z0-9_.]
CENSOR_REGEX = re.compile(
    # emails
    r"^$|\S+@\S+\.\S+"
    # instagram username
    r"|@[\w.]+"
    # european phone numbers
    r"|\+?\d{1,3}[ \-]?[(]?\d{3,4}[)]?[ \-]?\d{3,4}[ \-]?\d{3,4}",
    # URL adresses SIMPLIFIED
    # r"(https?://)?([a-z\d_\-]{3,}\.)+[a-z]{2,4}(/\S*)?"
    re.VERBOSE | re.IGNORECASE,
)


@register.filter
def censor_description(description: str) -> str:
    return CENSOR_REGEX.sub("---censored---", description)


@register.simple_tag(takes_context=True)
def get_current_pickup_request_of_user(context):
    request: HttpRequest = context["request"]

    try:
        return request.membership.user.pickup_system_issued_requests.filter(
            responsible_section=request.membership.section,
        ).latest("created")
    except PickupRequest.DoesNotExist:
        return None


@register.simple_tag(takes_context=True)
def get_waiting_requests_to_match(context):
    request: HttpRequest = context["request"]

    # pickup_system_plugin: Plugin = request.membership.section.plugins.get(
    #     app_label=all_plugins_mapped_to_class().get(PickupSystemConfig).label
    # )

    return PickupRequest.objects.filter(
        responsible_section=request.membership.section,
        state=PickupRequest.State.CREATED,
    )


@register.simple_tag(takes_context=True)
def get_waiting_pickup_requests_placed_before(context, br: PickupRequest):
    request: HttpRequest = context["request"]

    return request.membership.section.pickup_system_requests.filter(
        state=PickupRequest.State.CREATED,
        created__lt=br.created,
    ).count()


@register.simple_tag(takes_context=True)
def get_matched_pickup_requests(context):
    request: HttpRequest = context["request"]

    # TODO: limit by semester / time
    return request.user.pickup_system_request_matches.filter(
        request__responsible_section=request.membership.section,
        request__state=PickupRequest.State.MATCHED,
    ).order_by("-created")


@register.filter
def request_state_to_css_variant(state: PickupRequest.State):
    return {
        PickupRequest.State.CREATED: "info",
        PickupRequest.State.MATCHED: "success",
        PickupRequest.State.CANCELLED: "danger",
    }.get(state)


@register.simple_tag(takes_context=True)
def get_pickup_system_configuration(context):
    request: HttpRequest = context["request"]

    pickup_system_plugin: Plugin = request.in_space_of_section.plugins.get(
        app_label=all_plugins_mapped_to_class().get(PickupSystemConfig).label
    )

    return pickup_system_plugin.configuration
