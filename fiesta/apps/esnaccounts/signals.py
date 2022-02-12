from allauth.socialaccount import signals
from allauth.socialaccount.models import SocialLogin

from apps.esnaccounts.provider import ESNAccountsProvider
from apps.plugins.middleware.plugin import HttpRequest


def on_social_account_change(
        *,
        request: HttpRequest,
        sociallogin: SocialLogin,
        **kwargs,
):
    if sociallogin.account.provider == ESNAccountsProvider.id:
        ESNAccountsProvider.update_section_membership(
            request=request,
            sociallogin=sociallogin,
        )


signals.social_account_added.connect(on_social_account_change, dispatch_uid='update_section_membership')
signals.social_account_updated.connect(on_social_account_change, dispatch_uid='update_section_membership')
