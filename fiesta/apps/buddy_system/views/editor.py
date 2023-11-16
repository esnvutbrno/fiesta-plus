from __future__ import annotations

from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import UpdateView
from django_tables2 import TemplateColumn
from django_tables2.columns.base import LinkTransform
from django_tables2.utils import Accessor

from apps.buddy_system.forms import BuddyRequestEditorForm, QuickBuddyMatchForm
from apps.buddy_system.models import BuddyRequest, BuddyRequestMatch
from apps.fiestaforms.views.htmx import HtmxFormMixin
from apps.fiestarequests.tables.editor import BaseRequestsFilter, BaseRequestsTable
from apps.fiestarequests.views.editor import BaseQuickRequestMatchView
from apps.fiestatables.views.tables import FiestaTableView
from apps.sections.middleware.section_space import HttpRequest
from apps.sections.views.mixins.membership import EnsurePrivilegedUserViewMixin
from apps.utils.breadcrumbs import with_breadcrumb, with_object_breadcrumb
from apps.utils.views import AjaxViewMixin


class BuddyRequestsTable(BaseRequestsTable):
    match_request = TemplateColumn(
        template_name="buddy_system/parts/requests_editor_match_btn.html",
        exclude_from_export=True,
        order_by="match",
    )

    class Meta(BaseRequestsTable.Meta):
        fields = BaseRequestsTable.Meta.fields + ("match_request",)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "issuer_name" in self.columns:
            # sometimes excluded
            self.columns["issuer_name"].link = LinkTransform(
                attrs={"x-data": lambda: "modal($el.href)", "x-bind": "bind"},
                reverse_args=("buddy_system:editor-detail", {"pk": Accessor("pk")}),
            )


@with_breadcrumb(_("Buddy System"))
@with_breadcrumb(_("Requests"))
class BuddyRequestsEditorView(
    EnsurePrivilegedUserViewMixin,
    FiestaTableView,
):
    request: HttpRequest
    table_class = BuddyRequestsTable
    filterset_class = BaseRequestsFilter

    def get_queryset(self):
        return self.request.in_space_of_section.buddy_system_requests.select_related(
            "issuer__profile",
        )


@with_breadcrumb(_("Buddy System"))
@with_object_breadcrumb()
class BuddyRequestEditorDetailView(
    EnsurePrivilegedUserViewMixin,
    SuccessMessageMixin,
    HtmxFormMixin,
    AjaxViewMixin,
    UpdateView,
):
    template_name = "fiestaforms/pages/card_page_for_ajax_form.html"
    ajax_template_name = "fiestaforms/parts/ajax-form-container.html"
    model = BuddyRequest
    form_class = BuddyRequestEditorForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been updated.")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form_url"] = reverse("pickup_system:editor-detail", kwargs={"pk": self.object.pk})
        return context


@with_breadcrumb(_("Quick Buddy Match"))
@with_object_breadcrumb()
class QuickBuddyMatchView(BaseQuickRequestMatchView):
    model = BuddyRequest
    form_class = QuickBuddyMatchForm

    success_url = reverse_lazy("buddy_system:requests")
    success_message = _("Buddy request has been matched.")

    form_url = "buddy_system:quick-match"
    match_model = BuddyRequestMatch
