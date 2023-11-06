from __future__ import annotations

import typing

from django.db import models
from django.db.models import Manager

if typing.TYPE_CHECKING:
    from apps.fiestarequests.models.request import BaseRequestMatchProtocol, BaseRequestProtocol


class BaseRequestManager(Manager):
    model: BaseRequestProtocol | models.Model


class BaseRequestMatchManager(Manager):
    model: BaseRequestMatchProtocol | models.Model
