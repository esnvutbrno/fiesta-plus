from __future__ import annotations

import uuid

from django.contrib import messages
from django.db import models, transaction
from django.utils.translation import gettext as _
from django.views.generic.detail import BaseDetailView
from django_htmx.http import HttpResponseClientRedirect

from apps.fiestarequests.models.request import BaseRequestMatchProtocol, BaseRequestProtocol
from apps.sections.views.mixins.membership import EnsureLocalUserViewMixin
from apps.sections.views.mixins.section_space import EnsureInSectionSpaceViewMixin


class BaseTakeRequestView(EnsureInSectionSpaceViewMixin, EnsureLocalUserViewMixin, BaseDetailView):
    match_model: type[BaseRequestMatchProtocol] | type[models.Model]

    @transaction.atomic
    def post(self, request, pk: uuid.UUID):
        br: BaseRequestProtocol = self.get_object()

        match = self.match_model(
            request=br,
            matcher=self.request.user,
            # not null since enabling pickup system requires a faculty
            matcher_faculty=self.request.user.profile.faculty,
            note=self.request.POST.get("note") or "",
        )

        # TODO: check matcher relation to responsible section
        # TODO: reset any previous match for this BR
        match.save()

        br.match = match
        br.state = BaseRequestProtocol.State.MATCHED
        br.save(update_fields=["state"])

        messages.success(request, _("Request successfully matched!"))
        # TODO: target URL?
        return HttpResponseClientRedirect("/")
