from __future__ import annotations


class AuthConfigMixin:
    AUTH_PASSWORD_VALIDATORS = [
        {
            "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
        },
        {
            "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
        },
    ]

    AUTH_USER_MODEL = "accounts.User"

    # TODO: check, which settings are needed
    AUTHENTICATION_BACKENDS = (
        "django.contrib.auth.backends.ModelBackend",
        "allauth.account.auth_backends.AuthenticationBackend",
    )

    PASSWORD_HASHERS = [
        "django.contrib.auth.hashers.PBKDF2PasswordHasher",
        "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
        "django.contrib.auth.hashers.Argon2PasswordHasher",
        "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
        "django.contrib.auth.hashers.ScryptPasswordHasher",
        "apps.accounts.hashers.LegacyBCryptSHA256PasswordHasher",
    ]

    SOCIALACCOUNT_PROVIDERS = {
        "facebook": {
            "METHOD": "oauth2",
            "SDK_URL": "//connect.facebook.net/{locale}/sdk.js",
            "SCOPE": ["email", "public_profile"],
            # 'AUTH_PARAMS': {'auth_type': 'reauthenticate'},
            "INIT_PARAMS": {"cookie": True},
            "FIELDS": [
                "id",
                "first_name",
                "last_name",
                "name",
                "name_format",
                "picture",
                "short_name",
            ],
            "EXCHANGE_TOKEN": True,
            "LOCALE_FUNC": lambda request: "en",
            "VERIFIED_EMAIL": False,
            "VERSION": "v12.0",
        },
        "esnaccounts": {},
        "google": {
            "SCOPE": [
                "profile",
                "email",
            ],
            "AUTH_PARAMS": {
                "access_type": "online",
            },
        },
    }

    # configuration for fiesta accounts
    ACCOUNT_AUTHENTICATION_METHOD = "username_email"  # email or username
    ACCOUNT_SESSION_REMEMBER = None  # ask user for `remember`
    ACCOUNT_ADAPTER = "apps.accounts.adapters.AccountAdapter"
    ACCOUNT_EMAIL_REQUIRED = True  # email ftw
    ACCOUNT_USERNAME_REQUIRED = False  # email ftw
    ACCOUNT_DEFAULT_HTTP_PROTOCOL = "https"

    ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    SOCIALACCOUNT_EMAIL_VERIFICATION = "optional"
    # social account settings
    SOCIALACCOUNT_AUTO_SIGNUP = True  # after social login, do not enforce a signup form (only in case of conflict)
    SOCIALACCOUNT_ADAPTER = "apps.accounts.adapters.SocialAccountAdapter"
    # general django urls
    LOGIN_URL = "/auth/login"
    LOGIN_REDIRECT_URL = "/accounts/after-login"

    ACCOUNT_LOGIN_ON_PASSWORD_RESET = False  # do not autologin after password reset
    ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True  # logout after password change
    ACCOUNT_USERNAME_MIN_LENGTH = 4  # a personal preference
