from __future__ import annotations

import typing

import requests
from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider
from django.core.files.base import ContentFile
from django.http import HttpRequest
from django.utils.text import slugify

from apps.accounts.models import User, UserProfile
from apps.accounts.models.profile import user_profile_picture_storage
from apps.esnaccounts import logger
from apps.sections.models import Section, SectionMembership

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialAccount, SocialLogin


class ESNAccountsAccount(ProviderAccount):
    accounts: SocialAccount

    def get_avatar_url(self):
        sa: "SocialAccount" = self.account
        return sa.extra_data.get("picture")

    def __str__(self):
        return self.account.uid


class ESNAccountsProvider(CASProvider):
    id = "esnaccounts"
    name = "ESN Accounts"
    account_class = ESNAccountsAccount

    def extract_common_fields(self, data):
        uid, extra = data
        return {
            "username": extra.get("username", uid),
            "email": extra.get("mail"),
            "first_name": extra.get("first"),
            "last_name": extra.get("last"),
        }

    MEMBER_ROLE = "Local.activeMember"
    EDITOR_ROLE = "Local.regularBoardMember"

    @classmethod
    def update_section_membership(
        cls,
        *,
        request: HttpRequest,
        sociallogin: "SocialLogin",
    ):
        user: User = sociallogin.user
        sa: SocialAccount = sociallogin.account
        roles = sa.extra_data.get("roles", [])
        section_code = sa.extra_data.get("sc")
        section_name = sa.extra_data.get("section")
        user_nationality = sa.extra_data.get("nationality")
        # national_section = sa.extra_data.get("country")

        SectionMembership.objects.update_or_create(
            user=user,
            section=Section.objects.get_or_create(
                name=section_name,
                defaults=dict(
                    code=section_code,
                    # TODO: definitely not, user nationality != section assignment
                    country=user_nationality,
                    space_slug=slugify(section_name).lower().replace('-', '')
                ),
            )[0],
            defaults=dict(
                # we trust ESN Acccounts, so directly active membership
                # TODO: should be as AccountsConfiguration attribute, so section can select
                #  if they want to trust
                state=SectionMembership.State.ACTIVE,
                # TODO: check all possible for ESN Accounts roles
                role=SectionMembership.Role.EDITOR
                if cls.EDITOR_ROLE in roles
                else SectionMembership.Role.MEMBER
                if cls.MEMBER_ROLE in roles
                else SectionMembership.Role.INTERNATIONAL,
            ),
        )

        user_profile, _ = UserProfile.objects.update_or_create(
            user=user,
            defaults=dict(
                nationality=user_nationality,
                gender={
                    "M": "male",
                    "F": "female",
                }.get(sa.extra_data.get("gender")),
                state=UserProfile.State.INCOMPLETE,
            ),
        )

        cls.sync_profile_picture(
            profile=user_profile,
            picture_url=sa.extra_data.get("picture"),
        )

    @staticmethod
    def sync_profile_picture(profile: UserProfile, picture_url: str | None):
        if not picture_url:
            return

        picture_response = requests.get(
            picture_url,
            headers={
                "User-Agent": "Buena Fiesta; @esnvutbrno/buena-fiesta",
                # 'From': 'youremail@domain.com',
            },
        )

        if not picture_response.ok:
            logger.warn(
                "Picture request %s for user profile %s failed.", picture_url, profile
            )
            return

        name = user_profile_picture_storage.upload_to(profile, "--dummy--")

        name = user_profile_picture_storage.save(
            name, ContentFile(picture_response.content)
        )
        profile.picture = name
        profile.save(update_fields=["picture"], skip_hooks=True)


provider_classes = [ESNAccountsProvider]
