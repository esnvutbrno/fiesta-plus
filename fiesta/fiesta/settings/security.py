class SecurityConfigMixin:
    SECURE_PROXY_SSL_HEADER = "HTTP_X_FORWARDED_SSL", "on"
    CSRF_TRUSTED_ORIGINS = ["https://*.localhost"]

    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
