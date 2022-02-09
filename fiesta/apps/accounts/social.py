from allauth.socialaccount.models import SocialAccount, SocialLogin
from django.http import HttpRequest
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from apps.esnaccounts.provider import ESNAccountsProvider


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request: HttpRequest, login: SocialLogin):

        sa: SocialAccount = login.account
        if sa.provider == ESNAccountsProvider.id:
            ESNAccountsProvider.pre_social_login(request, login)
