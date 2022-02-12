from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.http import HttpRequest
from django_htmx.http import HttpResponseClientRedirect

from apps.esnaccounts.provider import ESNAccountsProvider


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request: HttpRequest, login: SocialLogin):
        sa: SocialAccount = login.account
        if sa.provider == ESNAccountsProvider.id:
            ESNAccountsProvider.pre_social_login(request, login)


class AccountAdapter(DefaultAccountAdapter):
    def is_ajax(self, request: HttpRequest):
        return super().is_ajax(request) or request.htmx

    def ajax_response(self, request, response, redirect_to=None, form=None, data=None):
        if not request.htmx or not redirect_to:
            return super().ajax_response(request, response, redirect_to=redirect_to, form=form, data=data)

        if redirect_to:
            return HttpResponseClientRedirect(redirect_to=redirect_to)
