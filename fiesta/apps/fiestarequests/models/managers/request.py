from __future__ import annotations

import typing

from django.db import models
from django.db.models import Manager

if typing.TYPE_CHECKING:
    from apps.fiestarequests.models.request import BaseRequestProtocol


class BaseRequestManager(Manager):
    model: BaseRequestProtocol | models.Model
