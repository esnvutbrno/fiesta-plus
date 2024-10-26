from __future__ import annotations

import re

from django import template

from apps.fiestarequests.models.request import BaseRequestProtocol

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


@register.filter
def request_state_to_css_variant(state: BaseRequestProtocol.State):
    return {
        BaseRequestProtocol.State.CREATED: "info hidden",
        BaseRequestProtocol.State.MATCHED: "success",
        BaseRequestProtocol.State.CANCELLED: "danger",
    }.get(state)
