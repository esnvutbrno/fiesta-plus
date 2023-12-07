from __future__ import annotations


class DatabaseConfigMixin:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "HOST": "db",
            "USER": "fiesta",
            "NAME": "fiesta",
            "PASSWORD": "fiesta",
        },
        "legacydb": {
            "ENGINE": "django.db.backends.mysql",
            "HOST": "legacydb",
            "NAME": "fiesta",
            # TODO: access to legacy db by standard user
            "USER": "root",
            "PASSWORD": "root",
        },
        "wiki": {
            "ENGINE": "django.db.backends.sqlite3",
            # TODO: pass from ENV
            "NAME": "/usr/src/wiki/db/wiki.sqlite3",
        },
    }
