from __future__ import annotations

from configurations.values import BooleanValue, PositiveIntegerValue, SecretValue, Value

from ._utils import BaseConfigurationProtocol


class DatabaseSmtpMailerConfigMixin(BaseConfigurationProtocol):
    MAILER_PRIMARY_BACKEND = Value(default="django.core.mail.backends.smtp.EmailBackend")
    MAILER_PRIMARY_TIMEOUT = PositiveIntegerValue(default=10, cast=int)
    MAILER_PRIMARY_HOST_USE_TLS = BooleanValue(default=True)
    MAILER_PRIMARY_HOST = SecretValue()
    MAILER_PRIMARY_HOST_PORT = SecretValue()
    MAILER_PRIMARY_HOST_PASSWORD = SecretValue()
    MAILER_PRIMARY_HOST_USER = SecretValue()

    # cannot use file, because pods
    MAILER_USE_FILE_LOCK = BooleanValue(default=False)

    # backend used by django itself
    EMAIL_BACKEND = Value(default="mailer.backend.DbBackend")

    # mailer used by db mailer to actually send emails
    @property
    def MAILER_EMAIL_BACKEND(self):
        return self.MAILER_PRIMARY_BACKEND

    @property
    def EMAIL_TIMEOUT(self):
        return self.MAILER_PRIMARY_TIMEOUT

    @property
    def EMAIL_HOST(self):
        return self.MAILER_PRIMARY_HOST

    @property
    def EMAIL_PORT(self):
        return self.MAILER_PRIMARY_HOST_PORT

    @property
    def EMAIL_HOST_USER(self):
        return self.MAILER_PRIMARY_HOST_USER

    @property
    def EMAIL_HOST_PASSWORD(self):
        return self.MAILER_PRIMARY_HOST_PASSWORD

    @property
    def EMAIL_USE_TLS(self):
        return self.MAILER_PRIMARY_HOST_USE_TLS
