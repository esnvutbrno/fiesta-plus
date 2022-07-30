from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_filters import ChoiceFilter
from django_tables2 import tables, Column
from django_tables2.utils import Accessor

from apps.buddy_system.forms import BuddyRequestEditorForm
from apps.buddy_system.models import BuddyRequest
from apps.fiestatables.columns import ImageColumn
from apps.fiestatables.filters import BaseFilterSet, ProperDateFromToRangeFilter
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.middleware.section_space import HttpRequest
from apps.sections.views.permissions import UserIsPrivilegedInCurrentSectionMixin
from apps.utils.breadcrumbs import with_breadcrumb
from apps.utils.views import AjaxViewMixin


class RequestFilter(BaseFilterSet):
    state = ChoiceFilter(choices=BuddyRequest.State.choices)
    created_when = ProperDateFromToRangeFilter(field_name="created")

    class Meta(BaseFilterSet.Meta):
        pass


class RequestTable(tables.Table):
    issuer__get_full_name = Column(
        order_by=("issuer__last_name", "issuer__first_name", "issuer__username"),
        attrs={"a": {"x-data": lambda: "modal($el.href)", "x-bind": "bind"}},
        linkify=("buddy_system:editor-detail", {"pk": Accessor("pk")}),
    )

    issuer__profile__picture = ImageColumn()

    class Meta:
        model = BuddyRequest
        # TODO: dynamic by section preferences
        fields = ("issuer", "state", "created")
        sequence = ("issuer__get_full_name", "issuer__profile__picture", "...")

        attrs = dict(tbody={"hx-disable": True})


@with_breadcrumb(_("Buddy System"))
@with_breadcrumb(_("Requests"))
class RequestsEditorView(
    UserIsPrivilegedInCurrentSectionMixin,
    FiestaTableView,
):
    request: HttpRequest
    table_class = RequestTable
    filterset_class = RequestFilter

    def get_queryset(self):
        return BuddyRequest.objects.filter(
            responsible_section=self.request.in_space_of_section
        ).select_related("issuer__profile")


class RequestEditorDetailView(
    UserIsPrivilegedInCurrentSectionMixin,
    SuccessMessageMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "buddy_system/editor/detail.html"
    ajax_template_name = "buddy_system/editor/detail_ajax.html"
    request: HttpRequest
    model = BuddyRequest
    form_class = BuddyRequestEditorForm

    success_url = reverse_lazy("buddy_system:requests-editor")
    success_message = _("Buddy request has been updated.")
