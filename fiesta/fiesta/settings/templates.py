from . import BaseConfigurationProtocol


class TemplatesConfigMixin(BaseConfigurationProtocol):
    FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

    def TEMPLATES(self):
        return [
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [self.BASE_DIR / "templates"],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": [
                        "django.template.context_processors.debug",
                        "django.template.context_processors.request",
                        "django.contrib.auth.context_processors.auth",
                        "django.contrib.messages.context_processors.messages",
                    ],
                },
            },
        ]
