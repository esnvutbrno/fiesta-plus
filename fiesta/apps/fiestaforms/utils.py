from django.forms import BaseForm


def make_form_disabled(form: BaseForm) -> BaseForm:
    """
    Iterates for all the field of forms and sets them as disabled.
    """
    for f in form.fields.values():
        f.disabled = True
    return form
