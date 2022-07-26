from __future__ import annotations

from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest as DjHttpRequest
from django_htmx.middleware import HtmxDetails

from apps.accounts.models import User


class HttpRequest(DjHttpRequest):
    htmx: HtmxDetails
    user: User | AnonymousUser
