from allauth_cas.urls import default_urlpatterns

from .provider import ESNAccountsProvider

urlpatterns = default_urlpatterns(ESNAccountsProvider)
