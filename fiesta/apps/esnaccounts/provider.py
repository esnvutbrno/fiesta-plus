from __future__ import annotations

import typing

import requests
from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpRequest
from django.utils.text import slugify
from phonenumber_field.phonenumber import to_python

from apps.accounts.models import User, UserProfile
from apps.accounts.models.profile import user_profile_picture_storage
from apps.accounts.services.user_profile_state_synchronizer import synchronizer
from apps.esnaccounts import logger
from apps.sections.models import Section, SectionMembership
from apps.sections.models.services.section_plugins_reconciler import SectionPluginsReconciler

if typing.TYPE_CHECKING:
    from allauth.socialaccount.models import SocialAccount, SocialLogin


class ESNAccountsAccount(ProviderAccount):
    accounts: SocialAccount

    def get_avatar_url(self):
        sa: SocialAccount = self.account
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
    ADMIN_ROLE = "Local.president"

    @classmethod
    @transaction.atomic
    def update_section_membership(
        cls,
        *,
        request: HttpRequest,
        sociallogin: SocialLogin,
    ):
        user: User = sociallogin.user
        sa: SocialAccount = sociallogin.account
        roles = sa.extra_data.get("roles", [])
        section_code = sa.extra_data.get("sc")
        section_name = sa.extra_data.get("section")
        user_nationality = sa.extra_data.get("nationality")
        # national_section = sa.extra_data.get("country")

        section, is_section_new = Section.objects.get_or_create(
            code=section_code,
            defaults=dict(
                name=section_name,
                # TODO: definitely not, user nationality != section assignment
                country=user_nationality,
                space_slug=slugify(section_name).lower().replace("-", ""),
            ),
        )

        SectionPluginsReconciler.reconcile(section)

        already_has_admin_user = section.memberships.filter(role=SectionMembership.Role.ADMIN).exists()
        promote_editor_to_admin = not already_has_admin_user or is_section_new

        # role and activation only for first time
        SectionMembership.objects.get_or_create(
            user=user,
            section=section,
            defaults=dict(
                # we trust ESN Acccounts, so directly active membership
                # TODO: should be as AccountsConfiguration attribute, so section can select
                #  if they want to trust
                state=SectionMembership.State.ACTIVE,
                role=(
                    SectionMembership.Role.ADMIN
                    if cls.ADMIN_ROLE in roles or (promote_editor_to_admin and cls.EDITOR_ROLE in roles)
                    else (
                        SectionMembership.Role.EDITOR
                        if cls.EDITOR_ROLE in roles
                        else (
                            SectionMembership.Role.MEMBER
                            if cls.MEMBER_ROLE in roles
                            else SectionMembership.Role.INTERNATIONAL
                        )
                    )
                ),
            ),
        )

        try:
            phone_number = to_python(sa.extra_data.get("telephone"))
        except TypeError:
            phone_number = None

        user_profile, _ = UserProfile.objects.update_or_create(
            user=user,
            defaults=dict(
                nationality=user_nationality,
                gender={
                    "M": "male",
                    "F": "female",
                }.get(sa.extra_data.get("gender")),
                state=UserProfile.State.INCOMPLETE,
                phone_number=phone_number,
            ),
        )

        cls.sync_profile_picture(
            profile=user_profile,
            picture_url=sa.extra_data.get("picture"),
        )

        synchronizer.revalidate_user_profile(user_profile)

    @staticmethod
    def sync_profile_picture(profile: UserProfile, picture_url: str | None):
        if not picture_url:
            return

        if profile.picture:
            logger.info("User profile %s already has a picture.", profile)
            return

        picture_response = requests.get(
            picture_url,
            headers={
                "User-Agent": "Fiesta+; @esnvutbrno/fiesta-plus",
            },
            timeout=(3, 5),
        )

        if not picture_response.ok:
            logger.warn("Picture request %s for user profile %s failed.", picture_url, profile)
            return

        name = user_profile_picture_storage.upload_to(profile, "--dummy--")

        name = user_profile_picture_storage.save(name, ContentFile(picture_response.content))
        profile.picture = name
        profile.save(update_fields=["picture"], skip_hooks=True)


provider_classes = [ESNAccountsProvider]
