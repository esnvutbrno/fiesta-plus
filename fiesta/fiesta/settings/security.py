from configurations.values import SecretValue


class SecurityConfigMixin:
    SECRET_KEY = SecretValue()

    SECURE_PROXY_SSL_HEADER = "HTTP_X_FORWARDED_SSL", "on"
    CSRF_TRUSTED_ORIGINS = ["https://*.localhost"]

    # TODO: probably dynamic?
    SESSION_COOKIE_DOMAIN = '.fiesta.localhost'

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
