from __future__ import annotations

import logging
from urllib.parse import parse_qs, urlparse

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from phonenumber_field.phonenumber import to_python
from phonenumbers import PhoneNumberFormat

logger = logging.getLogger(__name__)


def _first_part_in_path(path: str) -> str:
    return path.lstrip("/").partition("/")[0]


def clean_facebook(value: str) -> str:
    if not value:
        return ""

    try:
        parsed = urlparse(value)
    except ValueError:
        return value

    fb_id = parse_qs(parsed.query).get("id")
    if fb_id:
        return fb_id[0]

    return _first_part_in_path(parsed.path)


def clean_instagram(value: str) -> str:
    if not value:
        return ""

    try:
        parsed = urlparse(value)
    except ValueError:
        return value

    return _first_part_in_path(parsed.path)


def clean_telegram(value: str) -> str:
    if not value:
        return ""

    try:
        parsed = urlparse(value.removeprefix("t.me"))
    except ValueError:
        return value

    return _first_part_in_path(parsed.path)


def clean_whatsapp(value: str) -> str:
    if not value:
        return ""

    try:
        phone = to_python("+" + value.removeprefix("+"))
        if not phone or not phone.is_valid():
            raise TypeError("Not a phone number")

        return phone.format_as(PhoneNumberFormat.E164).removeprefix("+")
    except TypeError:
        try:
            parsed = urlparse(value)
            if parsed.netloc == "wa.me":
                return _first_part_in_path(parsed.path).removeprefix("+")
        except ValueError:
            pass

    raise ValidationError(_("Not a valid WhatsApp link"))
