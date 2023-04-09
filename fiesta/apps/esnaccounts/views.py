from __future__ import annotations

from allauth_cas.views import CASAdapter, CASCallbackView, CASLoginView, CASLogoutView

from .provider import ESNAccountsProvider


class ESNAccountsAdapter(CASAdapter):
    provider_id = ESNAccountsProvider.id
    url = "https://accounts.esn.org/cas/"
    version = 3


login = CASLoginView.adapter_view(ESNAccountsAdapter)

callback = CASCallbackView.adapter_view(ESNAccountsAdapter)

logout = CASLogoutView.adapter_view(ESNAccountsAdapter)
