from __future__ import annotations

from django import template

from apps.buddy_system.apps import BuddySystemConfig
from apps.buddy_system.models import BuddyRequest, BuddySystemConfiguration
from apps.plugins.middleware.plugin import HttpRequest
from apps.plugins.models import Plugin
from apps.plugins.utils import all_plugins_mapped_to_class

register = template.Library()


@register.simple_tag(takes_context=True)
def get_current_buddy_request_of_user(context):
    request: HttpRequest = context["request"]

    try:
        return request.membership.user.buddy_system_issued_requests.filter(
            responsible_section=request.membership.section,
        ).latest("created")
    except BuddyRequest.DoesNotExist:
        return None


@register.simple_tag(takes_context=True)
def get_waiting_requests_to_match(context):
    request: HttpRequest = context["request"]

    buddy_system_plugin: Plugin = request.membership.section.plugins.get(
        app_label=all_plugins_mapped_to_class().get(BuddySystemConfig).label
    )

    configuration: BuddySystemConfiguration = buddy_system_plugin.configuration

    return configuration.matching_policy_instance.limit_requests(
        qs=BuddyRequest.objects.filter(responsible_section=request.membership.section),
        membership=request.membership,
    )


@register.simple_tag(takes_context=True)
def get_waiting_buddy_requests_placed_before(context, br: BuddyRequest):
    request: HttpRequest = context["request"]

    return request.membership.section.buddy_system_requests.filter(
        state=BuddyRequest.State.CREATED,
        created__lt=br.created,
    ).count()


@register.simple_tag(takes_context=True)
def get_matched_buddy_requests(context):
    request: HttpRequest = context["request"]

    # TODO: limit by semester / time
    return request.user.buddy_system_request_matches.filter(
        request__responsible_section=request.membership.section,
        request__state=BuddyRequest.State.MATCHED,
    ).order_by("-created")


@register.simple_tag(takes_context=True)
def get_buddy_system_configuration(context):
    request: HttpRequest = context["request"]

    buddy_system_plugin: Plugin = request.in_space_of_section.plugins.get(
        app_label=all_plugins_mapped_to_class().get(BuddySystemConfig).label
    )

    return buddy_system_plugin.configuration
