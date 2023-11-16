from __future__ import annotations

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def sentry_js_loader_url():
    return getattr(settings, "SENTRY_JS_LOADER_URL", None)
