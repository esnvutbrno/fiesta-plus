from __future__ import annotations

from configurations.values import Value


class DatabaseConfigMixin:
    DATABASE_CONN_MAX_AGE = Value(default=5 * 60)
    DATABASE_CONN_HEALTH_CHECKS = Value(default=True)

    @property
    def DATABASES(self):
        return {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "HOST": "db",
                "USER": "fiesta",
                "NAME": "fiesta",
                "PASSWORD": "fiesta",
                "CONN_MAX_AGE": self.DATABASE_CONN_MAX_AGE,
                "CONN_HEALTH_CHECKS": self.DATABASE_CONN_HEALTH_CHECKS,
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
