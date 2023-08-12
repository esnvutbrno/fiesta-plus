from __future__ import annotations

from django import template

from apps.plugins.models import Plugin

register = template.Library()


@register.filter
def plugin_state_to_badge_css(state: Plugin.State):
    return {
        Plugin.State.ENABLED: "badge-success",
        Plugin.State.READ_ONLY: "badge-ghost",
        Plugin.State.PRIVILEGED_ONLY: "badge-info",
        Plugin.State.DISABLED: "badge-outline text-gray-600",
    }[state]
