from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider


class ESNAccountsAccount(ProviderAccount):
    pass


class ESNAccountsProvider(CASProvider):
    id = "esnaccounts"
    name = "ESN Accounts"
    account_class = ESNAccountsAccount

    # TODO: fix extract_common_fields to load data from extra_data


provider_classes = [ESNAccountsProvider]
