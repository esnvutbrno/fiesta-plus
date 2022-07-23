import typing

from django.db.models import QuerySet
from django.utils.translation import gettext_lazy as _

from apps.buddy_system.models import BuddyRequest
from apps.sections.models import SectionMembership


class MatchingPolicyProtocol(typing.Protocol):
    id: str
    title: str
    description: str
    can_member_match: bool

    @staticmethod
    def limit_requests(
        qs: typing.Union[QuerySet[BuddyRequest]], membership: SectionMembership
    ) -> typing.Union[QuerySet[BuddyRequest]]:
        ...

    def on_created_request(
        self,
        request: BuddyRequest,
    ) -> None:
        ...


class ManualByEditorMatchingPolicy(MatchingPolicyProtocol):
    id = "manual-by-editor"
    title = _("Manual by editors")
    description = _("Matching done manualy only by editors.")
    can_member_match = False


class ManualByMemberMatchingPolicy(MatchingPolicyProtocol):
    id = "manual-by-member"
    title = _("Manual by members")
    description = _("Matching done manualy also by members.")
    can_member_match = True


class SameFacultyMatchingPolicy(MatchingPolicyProtocol):
    id = "same-faculty"
    title = _("Limited by faculty")
    description = _(
        "Matching done manualy by members themselfs, but limited to the same faculty."
    )
    can_member_match = True


class LimitedSameFacultyMatchingPolicy(MatchingPolicyProtocol):
    id = "same-faculty-limited"
    title = _("Limited by faculty till limit")
    description = _(
        "Matching done manualy by members themselfs, but limited to same faculty till"
        "the rolling limit - limitation is not enabled after reaching the rolling limit."
    )

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

    DESCRIPTION = " <br />".join(
        f"{p.title}: {p.description}" for p in AVAILABLE_POLICIES
    )
