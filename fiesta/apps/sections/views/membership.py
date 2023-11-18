from __future__ import annotations

from _operator import attrgetter
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from django.views.generic import DetailView, RedirectView

from apps.accounts.models import User
from apps.buddy_system.apps import BuddySystemConfig
from apps.buddy_system.models import BuddyRequest
from apps.buddy_system.views.editor import BuddyRequestsTable
from apps.fiestatables.views.tables import FiestaMultiTableMixin
from apps.pickup_system.apps import PickupSystemConfig
from apps.pickup_system.models import PickupRequest
from apps.pickup_system.views.editor import PickupRequestsTable
from apps.plugins.views.mixins import CheckEnabledPluginsViewMixin
from apps.sections.models import SectionMembership
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin
from apps.utils.breadcrumbs import BreadcrumbItem, with_breadcrumb, with_callable_breadcrumb, with_object_breadcrumb
from apps.utils.models.query import get_single_object_or_none


def page_title(view: DetailView | View) -> BreadcrumbItem:
    m: SectionMembership = view.object
    return (
        BreadcrumbItem(
            title=_("Members"),
            url=reverse("sections:section-members"),
        )
        if m.is_local
        else BreadcrumbItem(
            title=_("Internationals"),
            url=reverse("sections:section-internationals"),
        )
    )


clean_list = lambda to_clean: list(filter(None, to_clean))


@with_breadcrumb(_("Section"))
@with_callable_breadcrumb(getter=page_title)
@with_object_breadcrumb(prefix=None, getter=attrgetter("user.full_name"))
class MembershipDetailView(
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    CheckEnabledPluginsViewMixin,
    FiestaMultiTableMixin,
    DetailView,
):
    model = SectionMembership
    object: SectionMembership
    template_name = "accounts/user_detail/user_detail.html"

    def get_context_data(self, **kwargs):
        bs_enabled = self._is_plugin_enabled_for_user(BuddySystemConfig)
        ps_enabled = self._is_plugin_enabled_for_user(PickupSystemConfig)

        data = super().get_context_data(**kwargs)
        data.update(
            {
                "table_titles": clean_list(
                    (
                        (_("🧑‍🤝‍🧑 Buddies") if self.object.is_local else _("🧑‍🤝‍🧑 Buddy requests"))
                        if bs_enabled
                        else None,
                        (_("📍 Pickups") if self.object.is_local else _("📍 Pickup requests")) if ps_enabled else None,
                    )
                ),
            }
        )
        return data

    def get_tables(self):
        bs_enabled = self._is_plugin_enabled_for_user(BuddySystemConfig)
        ps_enabled = self._is_plugin_enabled_for_user(PickupSystemConfig)

        if self.object.is_local:
            return clean_list(
                [
                    BuddyRequestsTable(
                        request=self.request,
                        data=BuddyRequest.objects.filter(match__matcher=self.object.user),
                        exclude=(
                            "matcher_name",
                            "matcher_picture",
                            "match_request",
                        ),
                    )
                    if bs_enabled
                    else None,
                    PickupRequestsTable(
                        request=self.request,
                        data=PickupRequest.objects.filter(match__matcher=self.object.user),
                        exclude=(
                            "matcher_name",
                            "matcher_picture",
                            "match_request",
                        ),
                    )
                    if ps_enabled
                    else None,
                ]
            )

        return clean_list(
            [
                BuddyRequestsTable(
                    request=self.request,
                    data=BuddyRequest.objects.filter(issuer=self.object.user),
                    exclude=(
                        "issuer_name",
                        "issuer_picture",
                        # "matcher_picture",
                        # "match_request",
                    ),
                )
                if bs_enabled
                else None,
                PickupRequestsTable(
                    request=self.request,
                    data=PickupRequest.objects.filter(issuer=self.object.user),
                    exclude=(
                        "issuer_name",
                        "issuer_picture",
                        # "matcher_picture",
                        # "match_request",
                    ),
                )
                if ps_enabled
                else None,
            ]
        )

    def get_queryset(self):
        return self.request.in_space_of_section.memberships


class UserDetailView(
    EnsurePrivilegedUserViewMixin,
    EnsureInSectionSpaceViewMixin,
    RedirectView,
):
    def get_redirect_url(self, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs.get("pk"))
        membership = get_single_object_or_none(
            self.request.in_space_of_section.memberships,
            user=user,
        )
        return reverse("sections:membership-detail", kwargs={"pk": membership.pk})
