from __future__ import annotations

from allauth_cas.views import CASAdapter, CASCallbackView, CASLoginView, CASLogoutView
from django.views.decorators.csrf import csrf_exempt

from .provider import ESNAccountsProvider


class ESNAccountsAdapter(CASAdapter):
    provider_id = ESNAccountsProvider.id
    url = "https://accounts.esn.org/cas/"
    version = 3


login = CASLoginView.adapter_view(ESNAccountsAdapter)

# see https://github.com/esnvutbrno/buena-fiesta/issues/228
callback = csrf_exempt(CASCallbackView.adapter_view(ESNAccountsAdapter))

logout = CASLogoutView.adapter_view(ESNAccountsAdapter)
