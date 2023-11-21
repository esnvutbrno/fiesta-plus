from __future__ import annotations

from configurations.values import SecretValue, Value

from ._utils import BaseConfigurationProtocol


class SmtpMailerConfigMixin(BaseConfigurationProtocol):
    MAILER_PRIMARY_BACKEND = Value(default="django.core.mail.backends.smtp.EmailBackend")
    MAILER_PRIMARY_TIMEOUT = Value(default=5)
    MAILER_PRIMARY_HOST_USE_TLS = Value(default=True)
    MAILER_PRIMARY_HOST = SecretValue()
    MAILER_PRIMARY_HOST_PORT = SecretValue()
    MAILER_PRIMARY_HOST_PASSWORD = SecretValue()
    MAILER_PRIMARY_HOST_USER = SecretValue()

    @property
    def EMAIL_BACKEND(self):
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
