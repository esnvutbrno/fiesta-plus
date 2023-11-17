from __future__ import annotations

from ._utils import BaseConfigurationProtocol


class TemplatesConfigMixin(BaseConfigurationProtocol):
    FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

    DJANGO_TABLES2_TEMPLATE = "fiestatables/django_tables2_table.html"

    def TEMPLATES(self):
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [
                    # to have "root" no-app templates
                    self.BASE_DIR / "templates",
                    # to allow to include "static" files in templates
                    # (e.g., svgs sometimes included and sometimes served as static files)
                    self.BASE_DIR / "static",
                ],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                        "django_admin_env_notice.context_processors.from_settings",
                    ],
                },
            },
        ]
