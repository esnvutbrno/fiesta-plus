from __future__ import annotations

import dataclasses
import typing
from typing import ClassVar

from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.fiestarequests.models import BaseRequestSystemConfiguration
from apps.sections.models import SectionMembership

if typing.TYPE_CHECKING:
    from apps.buddy_system.models import BuddyRequest


@dataclasses.dataclass
class BaseMatchingPolicy:
    conf: BaseRequestSystemConfiguration

    id: ClassVar[str]
    title: ClassVar[str]
    description: ClassVar[str]
    matching_done_by_members: ClassVar[bool]

    def limit_requests(self, qs: QuerySet[BuddyRequest], membership: SectionMembership) -> QuerySet[BuddyRequest]:
        # TODO: NotImplemented or base implementation?
        return qs.filter(self._base_filter(membership=membership)).select_related(
            "issuer",
            "issuer__profile",
            "issuer__profile__faculty",
            "issuer__profile__university",
        )

    def can_member_match(self, membership: SectionMembership) -> bool:
        if self.conf.rolling_limit == 0:
            return True
        from apps.buddy_system.models import BuddyRequestMatch

        matched_in_window = BuddyRequestMatch.objects.filter(
            request__responsible_section=membership.section,
            matcher=membership.user,
            created__gte=timezone.now() - self.conf.rolling_limit_window,
        ).count()

        return matched_in_window < self.conf.rolling_limit

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


class ManualByEditorMatchingPolicy(BaseMatchingPolicy):
    id = "manual-by-editor"
    title = _("Manual by editors")
    description = _("Matching is done manually only by editors.")
    matching_done_by_members = False


class ManualByMemberMatchingPolicy(BaseMatchingPolicy):
    id = "manual-by-member"
    title = _("Manual by members")
    description = _("Matching is done manually directly by members.")
    matching_done_by_members = True


class ManualWithSameFacultyMatchingPolicy(BaseMatchingPolicy):
    id = "same-faculty"
    title = _("Manual by members with restriction to same faculty")
    description = _("Matching is done manually by members themselves, but limited to the same faculty.")
    matching_done_by_members = True

    def limit_requests(self, qs: QuerySet[BuddyRequest], membership: SectionMembership) -> QuerySet[BuddyRequest]:
        from apps.accounts.models import UserProfile

        member_profile: UserProfile = membership.user.profile_or_none

        return qs.filter(self._base_filter(membership=membership)).filter(
            issuer_faculty=member_profile.faculty,
        )


class LimitedSameFacultyMatchingPolicy(BaseMatchingPolicy):
    id = "same-faculty-limited"
    title = _("Restricted to same faculty with limit")
    description = _(
        "Matching is done manually by members themselves, but limited to same faculty till"
        "the rolling limit - limitation is not enabled after reaching the limit."
    )
    matching_done_by_members = True

    # same faculty for N buddies
    # after N matches (to rolling_limit), faculty is not limited


class AutoMatchingPolicy(BaseMatchingPolicy):
    ...
    # by internationals' selected interests
    # request will be matched to one from buddies automatically
    # (or the 'match' will be proposed to editor to confirm it)


class MatchingPoliciesRegister:
    AVAILABLE_POLICIES = [
        ManualByEditorMatchingPolicy,
        ManualByMemberMatchingPolicy,
        ManualWithSameFacultyMatchingPolicy,
        # TODO: make it working
        # LimitedSameFacultyMatchingPolicy,
        # AutoMatchingPolicy
    ]

    DEFAULT_POLICY = ManualByEditorMatchingPolicy

    CHOICES = [(p.id, p.title) for p in AVAILABLE_POLICIES]

    DESCRIPTION = " <br />".join(f"{p.title}: {p.description}" for p in AVAILABLE_POLICIES)

    _ID_TO_POLICY: dict[str, type[BaseMatchingPolicy]] = {p.id: p for p in AVAILABLE_POLICIES}

    @classmethod
    def get_policy(
        cls,
        configuration: BaseRequestSystemConfiguration,
    ) -> BaseMatchingPolicy:
        return cls._ID_TO_POLICY.get(configuration.matching_policy, cls.DEFAULT_POLICY)(conf=configuration)
