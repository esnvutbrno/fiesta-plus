from __future__ import annotations

import typing

from django.db import models
from django.db.models import Manager

if typing.TYPE_CHECKING:
    from apps.accounts.models import User
    from apps.fiestarequests.models.request import BaseRequestProtocol


class BaseRequestManager(Manager):
    model: BaseRequestProtocol | models.Model

    def match_by(self, request: BaseRequestProtocol | models.Model, matcher: User):
        request.matched_by = matcher
        request.state = self.model.State.MATCHED

        # TODO: check matcher relation to responsible section?

        request.save(update_fields=["matched_by", "matched_at", "state"])
