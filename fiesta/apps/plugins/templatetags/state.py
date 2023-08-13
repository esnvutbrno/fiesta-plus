from __future__ import annotations

from django import template

from apps.plugins.models import Plugin

register = template.Library()


@register.filter
def plugin_state_to_badge_css(state: Plugin.State):
    return {
        Plugin.State.ENABLED: "btn-success",
        Plugin.State.READ_ONLY: "btn-ghost",
        Plugin.State.PRIVILEGED_ONLY: "btn-accent",
        Plugin.State.DISABLED: "btn-ghost",
    }.get(state)
