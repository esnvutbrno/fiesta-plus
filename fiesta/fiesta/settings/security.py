from __future__ import annotations

from configurations.values import SecretValue


class SecurityConfigMixin:
    ROOT_DOMAIN: str  # inherited from another mixin

    SECRET_KEY = SecretValue()

    SECURE_PROXY_SSL_HEADER = "HTTP_X_FORWARDED_SSL", "on"

    def CSRF_TRUSTED_ORIGINS(self):
        return [f"https://*.{self.ROOT_DOMAIN}"]

    def SESSION_COOKIE_DOMAIN(self):
        return f".{self.ROOT_DOMAIN}"

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
