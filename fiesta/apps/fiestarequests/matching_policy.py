from __future__ import annotations

import typing

from django.db.models import Q, QuerySet
from django.utils.translation import gettext_lazy as _

from apps.sections.models import SectionMembership

if typing.TYPE_CHECKING:
    from apps.buddy_system.models import BuddyRequest


class MatchingPolicyProtocol(typing.Protocol):
    id: str
    title: str
    description: str
    can_member_match: bool

    def limit_requests(self, qs: QuerySet[BuddyRequest], membership: SectionMembership) -> QuerySet[BuddyRequest]:
        # TODO: NotImplemented or base implementation?
        return qs.filter(self._base_filter(membership=membership)).select_related(
            "issuer",
            "issuer__profile",
            "issuer__profile__guest_faculty",
            "issuer__profile__home_university",
        )

    def on_created_request(
        self,
        request: BuddyRequest,
    ) -> None:
        ...

    @classmethod
    def _base_filter(cls, membership: SectionMembership) -> Q:
        from apps.buddy_system.models import BuddyRequest

        return Q(
            responsible_section=membership.section,
            state=BuddyRequest.State.CREATED,
            match__isnull=True,  # to be sure
        )


class ManualByEditorMatchingPolicy(MatchingPolicyProtocol):
    id = "manual-by-editor"
    title = _("Manual by editors")
    description = _("Matching is done manually only by editors.")
    can_member_match = False


class ManualByMemberMatchingPolicy(MatchingPolicyProtocol):
    id = "manual-by-member"
    title = _("Manual by members")
    description = _("Matching is done manually directly by members.")
    can_member_match = True


class SameFacultyMatchingPolicy(MatchingPolicyProtocol):
    id = "same-faculty"
    title = _("Restricted to same faculty")
    description = _("Matching is done manually by members themselves, but limited to the same faculty.")
    can_member_match = True

    def limit_requests(self, qs: QuerySet[BuddyRequest], membership: SectionMembership) -> QuerySet[BuddyRequest]:
        from apps.accounts.models import UserProfile

        member_profile: UserProfile = membership.user.profile_or_none

        return qs.filter(self._base_filter(membership=membership)).filter(
            issuer__profile__guest_faculty=member_profile.home_faculty,
        )


class LimitedSameFacultyMatchingPolicy(MatchingPolicyProtocol):
    id = "same-faculty-limited"
    title = _("Restricted to same faculty with limit")
    description = _(
        "Matching is done manually by members themselves, but limited to same faculty till"
        "the rolling limit - limitation is not enabled after reaching the limit."
    )
    can_member_match = True

    # same faculty for N buddies
    # after N matches (to rolling_limit), faculty is not limited


class AutoMatchingPolicy(MatchingPolicyProtocol):
    ...
    # by internationals' selected interests
    # request will be matched to one from buddies automatically
    # (or the 'match' will be proposed to editor to confirm it)


class MatchingPoliciesRegister:
    AVAILABLE_POLICIES = [
        ManualByEditorMatchingPolicy,
        ManualByMemberMatchingPolicy,
        SameFacultyMatchingPolicy,
        LimitedSameFacultyMatchingPolicy,
        # AutoMatchingPolicy
    ]

    DEFAULT_POLICY = ManualByEditorMatchingPolicy

    CHOICES = [(p.id, p.title) for p in AVAILABLE_POLICIES]

    DESCRIPTION = " <br />".join(f"{p.title}: {p.description}" for p in AVAILABLE_POLICIES)

    _ID_TO_POLICY = {p.id: p() for p in AVAILABLE_POLICIES}

    @classmethod
    def get_policy_by_id(cls, policy_id: str) -> MatchingPolicyProtocol:
        return cls._ID_TO_POLICY.get(policy_id)
