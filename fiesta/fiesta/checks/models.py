# flake8: noqa
"""
Copyright: https://hakibenita.com/automating-the-boring-stuff-in-django-using-the-check-framework

Custom models checks:
H001: Field has no verbose name.
H002: Verbose name should use gettext.
H003: Words in verbose name must be all upper case or all lower case.
H004: Help text should use gettext.
H005: Model must define class Meta.
H006: Model has no verbose name.
H007: Model has no verbose name plural.
H008: Must set db_index explicitly on a ForeignKey field.
"""
import ast
import inspect

import django.apps
import django.core.checks
from django.core.exceptions import FieldDoesNotExist


def get_argument(node, arg):
    for kw in node.value.keywords:
        if kw.arg == arg:
            return kw
    return None


def is_constant_node(node):
    if not isinstance(node, ast.Name):
        return False

    return node.id.replace("_", "").isupper()


def is_gettext_node(node):
    if not isinstance(node, ast.Call):
        return False

    # We assume gettext is aliased '_'.
    if node.func.id != "_":  # type: ignore
        return False

    return True


def check_model(model):
    """Check a single model.

    Yields (django.checks.CheckMessage)
    """
    model_source = inspect.getsource(model)
    model_node = ast.parse(model_source.strip())
    assert isinstance(model_node, ast.Module)

    class_meta = None
    for node in model_node.body[0].body:  # type: ignore
        if isinstance(node, ast.ClassDef):
            # class Meta
            if node.name == "Meta":
                class_meta = node

        # Fields
        elif isinstance(node, ast.Assign):
            if len(node.targets) != 1:
                continue

            if not isinstance(node.targets[0], ast.Name):
                continue

            field_name = node.targets[0].id
            try:
                field = model._meta.get_field(field_name)
            except FieldDoesNotExist:
                continue

            verbose_name = get_argument(node, "verbose_name")
            if verbose_name is None:
                yield django.core.checks.Warning(
                    "Field has no verbose name",
                    hint="Set verbose name on the field.",
                    obj=field,
                    id="H001",
                )

            else:
                if not is_gettext_node(verbose_name.value):
                    yield django.core.checks.Warning(
                        "Verbose name should use gettext",
                        hint="Use gettext on the verbose name.",
                        obj=field,
                        id="H002",
                    )

                else:
                    value = verbose_name.value.args[0].s  # type: ignore
                    if not all(
                        w.islower() or w.isupper() or w.isdigit()
                        for w in value.split(" ")
                    ):
                        yield django.core.checks.Warning(
                            "Words in verbose name must be all upper case or all lower case",
                            hint='Change verbose name to "{}".'.format(value.lower()),
                            obj=field,
                            id="H003",
                        )

            help_text = get_argument(node, "help_text")
            if help_text is not None:
                if not is_gettext_node(help_text.value) and not is_constant_node(
                    help_text.value
                ):
                    yield django.core.checks.Warning(
                        "Help text should use gettext",
                        hint="Use gettext on the help text.",
                        obj=field,
                        id="H004",
                    )

            if field.many_to_one:
                db_index = get_argument(node, "db_index")
                if db_index is None:
                    yield django.core.checks.Warning(
                        "Must set db_index explicitly on a ForeignKey field",
                        hint="Set db_index on the field ("
                        "https://hakibenita.com/9-django-tips-for-working-with-databases#fk-indexes).",
                        obj=field,
                        id="H008",
                    )

    if class_meta is None:
        yield django.core.checks.Warning(
            'Model "{}" must define class Meta'.format(model._meta.model_name),
            hint='Add class Meta to model "{}".'.format(model._meta.model_name),
            obj=model,
            id="H005",
        )

    else:
        verbose_name = None
        verbose_name_plural = None

        for node in ast.iter_child_nodes(class_meta):
            if not isinstance(node, ast.Assign):
                continue

            if not isinstance(node.targets[0], ast.Name):
                continue

            attr = node.targets[0].id

            if attr == "verbose_name":
                verbose_name = node

            if attr == "verbose_name_plural":
                verbose_name_plural = node

        if verbose_name is None:
            yield django.core.checks.Warning(
                "Model has no verbose name",
                hint="Add verbose_name to class Meta.",
                obj=model,
                id="H006",
            )

        elif not is_gettext_node(verbose_name.value):
            yield django.core.checks.Warning(
                "Verbose name in class Meta should use gettext",
                hint='Use gettext on the verbose_name of class Meta "{}".'.format(
                    model._meta.model_name
                ),
                obj=model,
                id="H002",
            )

        if verbose_name_plural is None:
            yield django.core.checks.Warning(
                "Model has no verbose name plural",
                hint="Add verbose_name_plural to class Meta.",
                obj=model,
                id="H007",
            )

        elif not is_gettext_node(verbose_name_plural.value):
            yield django.core.checks.Warning(
                "Verbose name plural in class Meta should use gettext",
                hint='Use gettext on the verbose_name_plural of class Meta "{}".'.format(
                    model._meta.model_name
                ),
                obj=model,
                id="H002",
            )


APPS_PREFIX_TO_INCLUDE = __name__.partition(".")[0]


@django.core.checks.register(django.core.checks.Tags.models)
def check_models(app_configs, **kwargs):
    errors = []
    for app in django.apps.apps.get_app_configs():
        # Skip third party apps.
        if "site-packages" in app.path:
            continue

        for model in app.get_models():
            for check_message in check_model(model):
                errors.append(check_message)

    return errors
