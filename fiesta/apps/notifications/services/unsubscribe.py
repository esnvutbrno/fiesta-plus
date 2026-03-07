from __future__ import annotations

import logging

from django.core.signing import BadSignature, TimestampSigner

logger = logging.getLogger(__name__)

UNSUBSCRIBE_SALT = "notifications-unsubscribe"


def generate_unsubscribe_token(user_id: int, action: str = "global") -> str:
    signer = TimestampSigner(salt=UNSUBSCRIBE_SALT)
    return signer.sign(f"{user_id}:{action}")


def verify_unsubscribe_token(token: str, max_age: int = 30 * 24 * 60 * 60) -> tuple[int, str]:
    signer = TimestampSigner(salt=UNSUBSCRIBE_SALT)
    value = signer.unsign(token, max_age=max_age)
    try:
        user_id_str, action = value.rsplit(":", 1)
        return int(user_id_str), action
    except (TypeError, ValueError) as exc:
        raise BadSignature("Invalid unsubscribe payload") from exc
