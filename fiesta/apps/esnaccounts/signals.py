from __future__ import annotations

from allauth.account import signals
from allauth.socialaccount import signals as signals_social
from allauth.socialaccount.models import SocialLogin

from apps.esnaccounts.provider import ESNAccountsProvider
from apps.plugins.middleware.plugin import HttpRequest


def on_social_account_change(
    *,
    request: HttpRequest,
    sociallogin: SocialLogin = None,
    **kwargs,
):
    if sociallogin and sociallogin.account.provider == ESNAccountsProvider.id:
        ESNAccountsProvider.update_section_membership(
            request=request,
            sociallogin=sociallogin,
        )


signals_social.social_account_added.connect(on_social_account_change, dispatch_uid="update_section_membership")
signals_social.social_account_updated.connect(on_social_account_change, dispatch_uid="update_section_membership")
signals.user_signed_up.connect(on_social_account_change, dispatch_uid="update_section_membership")
