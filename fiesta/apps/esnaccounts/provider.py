import typing

from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider
from django.http import HttpRequest

from apps.accounts.models import User
from apps.sections.models import Section, SectionMembership

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialAccount, SocialLogin


class ESNAccountsAccount(ProviderAccount):
    def get_avatar_url(self):
        sa: 'SocialAccount' = self.account
        return sa.extra_data.get('picture')


class ESNAccountsProvider(CASProvider):
    id = "esnaccounts"
    name = "ESN Accounts"
    account_class = ESNAccountsAccount

    def extract_common_fields(self, data):
        uid, extra = data
        return {
            'username': extra.get('username', uid),
            'email': extra.get('mail'),
            'first_name': extra.get('first'),
            'last_name': extra.get('last'),
        }

    MEMBER_ROLE = 'Local.activeMember'
    EDITOR_ROLE = 'Local.regularBoardMember'

    @classmethod
    def pre_social_login(
            cls,
            request: HttpRequest,
            login: 'SocialLogin',
    ):
        user: User = login.user
        sa: SocialAccount = login.account
        roles = sa.extra_data.get('roles', [])
        section_code = sa.extra_data.get('sc')
        section_name = sa.extra_data.get('section')
        user_nationality = sa.extra_data.get('nationality')
        national_section = sa.extra_data.get('country')

        user.save()
        SectionMembership.objects.update_or_create(
            user=user,
            section=Section.objects.get_or_create(
                name=section_name,
                defaults=dict(
                    code=section_code,
                    # TODO: definitely not, user nationality != section assignment
                    country=user_nationality,
                )
            )[0],
            defaults=dict(
                # TODO: check all possible for ESN Accounts roles
                state=SectionMembership.State.ACTIVE,
                role=SectionMembership.Role.EDITOR if cls.EDITOR_ROLE in roles
                else SectionMembership.Role.MEMBER if cls.MEMBER_ROLE in roles
                else SectionMembership.Role.INTERNATIONAL
            )
        )


provider_classes = [ESNAccountsProvider]
