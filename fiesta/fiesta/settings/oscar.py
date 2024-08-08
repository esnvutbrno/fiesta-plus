from __future__ import annotations

from oscar import defaults

BaseOscarConfigMixin = type(
    "OscarConfigMixin",
    (),
    {k: v for k, v in defaults.__dict__.items()},
)


class OscarConfigMixin(BaseOscarConfigMixin):
    HAYSTACK_CONNECTIONS = {
        "default": {
            "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
        },
    }

    OSCAR_INITIAL_ORDER_STATUS = "Pending"
    OSCAR_INITIAL_LINE_STATUS = "Pending"
    OSCAR_ORDER_STATUS_PIPELINE = {
        "Pending": (
            "Being processed",
            "Cancelled",
        ),
        "Being processed": (
            "Processed",
            "Cancelled",
        ),
        "Cancelled": (),
    }


__all__ = ["OscarConfigMixin"]
