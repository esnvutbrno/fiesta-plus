from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_tables2 import TemplateColumn, tables
from django_tables2.columns.base import Column, LinkTransform
from django_tables2.utils import Accessor

from apps.fiestaforms.views.htmx import HtmxFormViewMixin
from apps.fiestarequests.tables.editor import BaseRequestsFilter, BaseRequestsTable
from apps.fiestarequests.views.editor import BaseQuickRequestMatchView, BaseUpdateRequestStateView
from apps.fiestatables.views.tables import FiestaTableView
from apps.pickup_system.forms import PickupRequestEditorForm, QuickPickupMatchForm
from apps.pickup_system.models import PickupRequest, PickupRequestMatch
from apps.sections.middleware.section_space import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb, with_plugin_home_breadcrumb
from apps.utils.views import AjaxViewMixin


class PickupRequestsTable(BaseRequestsTable):
    match_request = TemplateColumn(
        template_name="pickup_system/parts/requests_editor_match_btn.html",
        exclude_from_export=True,
        order_by="match",
    )

    time = tables.columns.DateTimeColumn()

    place = Column(
        linkify=lambda record: record.location_as_google_maps_link,
    )

    class Meta(BaseRequestsTable.Meta):
        model = PickupRequest
        fields = BaseRequestsTable.Meta.fields + ("match_request",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "matcher_picture" in self.columns:
            self.columns["matcher_picture"].column.visible = False

        if "issuer_name" in self.columns:
            # sometimes excluded
            self.columns["issuer_name"].link = LinkTransform(
                attrs={"x-data": lambda: "modal($el.href)", "x-bind": "bind"},
                reverse_args=("pickup_system:editor-detail", {"pk": Accessor("pk")}),
            )


@with_plugin_home_breadcrumb
@with_breadcrumb(_("Requests"))
class PickupRequestsEditorView(
    EnsurePrivilegedUserViewMixin,
    FiestaTableView,
):
    request: HttpRequest
    table_class = PickupRequestsTable
    filterset_class = BaseRequestsFilter

    def get_queryset(self):
        return self.request.in_space_of_section.pickup_system_requests.select_related(
            "issuer__profile",
        )


@with_plugin_home_breadcrumb
@with_object_breadcrumb()
class PickupRequestEditorDetailView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormViewMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"
    model = PickupRequest
    form_class = PickupRequestEditorForm

    success_url = reverse_lazy("pickup_system:requests")
    success_message = _("Pickup request has been updated.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse("pickup_system:editor-detail", kwargs={"pk": self.object.pk})
        return context


class QuickPickupMatchView(BaseQuickRequestMatchView):
    model = PickupRequest
    form_class = QuickPickupMatchForm

    success_url = reverse_lazy("pickup_system:requests")
    success_message = _("Pickup request has been matched.")

    form_url = "pickup_system:quick-match"
    match_model = PickupRequestMatch


class UpdatePickupRequestStateView(BaseUpdateRequestStateView):
    model = PickupRequest
    object: PickupRequest

    success_url = reverse_lazy("pickup_system:requests")

    def get_queryset(self):
        return self.request.in_space_of_section.pickup_system_requests
