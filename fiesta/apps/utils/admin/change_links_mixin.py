from __future__ import annotations

from django.urls import reverse
from django_admin_relation_links.options import AdminChangeLinksMixin as DjAdminChangeLinksMixin, get_link_field


class AdminChangeLinksMixin(DjAdminChangeLinksMixin):
    def _get_app_model(self, instance, model_field_name, options):
        options_model = options.get("model")

        if options_model:
            if "." in options_model:
                app, model = options_model.lower().split(".")
            else:
                app = self.opts.app_label
                model = options_model.lower()
        else:
            # fixed here, removed `.model`
            model_meta = getattr(instance, model_field_name)._meta
            app = model_meta.app_label
            model = model_meta.model_name

        return app, model

    def _get_changelist_link(self, instance, model_field_name, options):
        def get_url():
            return reverse(
                "{}:{}_{}_changelist".format(
                    self.admin_site.name, *self._get_app_model(instance, model_field_name, options)
                )
            )

        def get_lookup_filter():
            return options.get("lookup_filter") or instance._meta.get_field(model_field_name).field.name

        def get_label():
            # fixed here, removed `.model`
            return options.get("label") or getattr(instance, model_field_name)._meta.verbose_name_plural.capitalize()

        return get_link_field(f"{get_url()}?{get_lookup_filter()}={instance.pk}", get_label())
