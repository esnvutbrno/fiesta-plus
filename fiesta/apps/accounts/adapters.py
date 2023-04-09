from __future__ import annotations

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.http import HttpRequest
from django_htmx.http import HttpResponseClientRedirect


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    ...


class AccountAdapter(DefaultAccountAdapter):
    def is_ajax(self, request: HttpRequest):
        return super().is_ajax(request) or request.htmx

    def ajax_response(self, request, response, redirect_to=None, form=None, data=None):
        if redirect_to:
            return HttpResponseClientRedirect(redirect_to=redirect_to)
        # do not send the JSON response, since we use the HTMX replacements with raw HTML
        return response

    # TODO: making usernames from first_name is kinda bleeh
    #  so generate_unique_username could be ovveriden here to compose username from last_name+smth?
